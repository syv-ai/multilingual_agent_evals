"""Benchmark the public MultiBFCL release with a local EuroEval dataset config.

This does not change EuroEval or rely on its possibly private derived mini datasets.
Model inference starts only when the script is invoked with a model ID.
"""

import argparse
import hashlib
import json
from functools import partial
from pathlib import Path

from datasets import Dataset, DatasetDict
from euroeval import Benchmarker, DatasetConfig
from euroeval.enums import GenerativeType
from euroeval.languages import DANISH, ENGLISH, FRENCH, GERMAN
from euroeval.tasks import TOOL_CALLING

LANGUAGES = {"da": DANISH, "en": ENGLISH, "de": GERMAN, "fr": FRENCH}
SOURCE = "syvai/multi-bfcl"


def _convert_row(row: dict[str, str]) -> dict[str, str]:
    """Format public MultiBFCL fields for EuroEval's tool-calling task.

    Args:
        row:
            Source row with JSON-encoded conversation, functions and answers.

    Returns:
        The text prompt, tool schema and reference calls.
    """
    messages = json.loads(row["question"])[0]
    if len(messages) == 1 and messages[0]["role"] == "user":
        question = f"Question: {messages[0]['content']}"
    else:
        role_labels = {"system": "System", "user": "Question", "assistant": "Assistant"}
        question = "\n".join(
            f"{role_labels.get(message['role'], message['role'].title())}: "
            f"{message['content']}"
            for message in messages
        )
    functions = json.dumps(json.loads(row["function"]), ensure_ascii=False)
    answers = json.dumps(json.loads(row["ground_truth"]), ensure_ascii=False)
    return {
        "text": f"Functions:\n{functions}\n{question}",
        "function": functions,
        "target_text": answers,
    }


def _preprocess(
    dataset: DatasetDict,
    max_examples: int | None = None,
    sample_ids: list[str] | None = None,
) -> DatasetDict:
    """Convert the public test split, optionally limiting a smoke run.

    Args:
        dataset:
            The released language subset with only a test split.
        max_examples (optional):
            Number of first examples for a smoke run. Defaults to None.
        sample_ids (optional):
            Ordered source IDs to evaluate across languages. Defaults to None.

    Returns:
        A test-only dataset in EuroEval's tool-calling format.

    Raises:
        ValueError:
            If a requested source ID is absent from the language subset.
    """
    test_split = dataset["test"]
    assert isinstance(test_split, Dataset)
    if sample_ids is not None:
        ids = test_split["id"]
        index_by_id = {source_id: index for index, source_id in enumerate(ids)}
        missing = set(sample_ids) - set(index_by_id)
        if missing:
            raise ValueError(f"Missing MultiBFCL source IDs: {sorted(missing)}")
        selected = test_split.select(
            [index_by_id[source_id] for source_id in sample_ids]
        )
        assert isinstance(selected, Dataset)
        test_split = selected
    elif max_examples is not None:
        selected = test_split.select(range(min(max_examples, len(test_split))))
        assert isinstance(selected, Dataset)
        test_split = selected
    converted = test_split.map(
        _convert_row,
        remove_columns=[column for column in test_split.column_names if column != "id"],
    )
    assert isinstance(converted, Dataset)
    return DatasetDict({"test": converted})


def main() -> None:
    """Run separate tool-calling scores for the selected models and languages."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", action="append", required=True, help="Model ID")
    parser.add_argument("--api-base", help="OpenAI-compatible inference API base URL")
    parser.add_argument(
        "--local-csv-dir",
        type=Path,
        help="Directory with <language>.csv test exports of the public Hub data",
    )
    parser.add_argument(
        "--generative-type",
        choices=("instruction_tuned", "reasoning"),
        help="Override EuroEval's model type (reasoning avoids JSON schema mode)",
    )
    parser.add_argument(
        "--max-generated-tokens",
        type=int,
        help="Requested token cap; proxies may ignore it (64 for smoke runs)",
    )
    parser.add_argument(
        "--language",
        choices=LANGUAGES,
        action="append",
        default=None,
        help="Language subset; defaults to da (repeat to add languages)",
    )
    parser.add_argument(
        "--max-examples",
        type=int,
        default=None,
        help="Smoke test only: use the first N examples (not a publishable score)",
    )
    parser.add_argument(
        "--sample-ids-file",
        type=Path,
        help="JSON list of ordered BFCL source IDs shared across languages",
    )
    parser.add_argument(
        "--num-iterations",
        type=int,
        default=1,
        help="Bootstrap iterations; defaults to one",
    )
    args = parser.parse_args()
    if args.max_examples is not None and args.max_examples < 1:
        parser.error("--max-examples must be positive")
    if args.max_generated_tokens is not None and args.max_generated_tokens < 1:
        parser.error("--max-generated-tokens must be positive")
    if args.num_iterations < 1:
        parser.error("--num-iterations must be positive")
    if args.max_examples is not None and args.sample_ids_file is not None:
        parser.error("Choose --max-examples or --sample-ids-file, not both")
    sample_ids = None
    if args.sample_ids_file is not None:
        sample_ids = json.loads(args.sample_ids_file.read_text(encoding="utf-8"))
        if (
            not isinstance(sample_ids, list)
            or not sample_ids
            or not all(isinstance(source_id, str) for source_id in sample_ids)
            or len(sample_ids) != len(set(sample_ids))
        ):
            parser.error("--sample-ids-file must contain distinct source ID strings")
    languages = list(dict.fromkeys(args.language or ["da"]))
    if args.local_csv_dir is not None:
        for code in languages:
            csv_path = args.local_csv_dir / f"{code}.csv"
            if not csv_path.is_file():
                parser.error(f"Missing BFCL test export: {csv_path}")
    sample_tag = (
        hashlib.sha256(json.dumps(sample_ids).encode("utf-8")).hexdigest()[:10]
        if sample_ids is not None
        else None
    )
    suffix = (
        f"-sample-{len(sample_ids)}-{sample_tag}"
        if sample_ids is not None
        else f"-smoke-{args.max_examples}"
        if args.max_examples
        else ""
    )
    configs = [
        DatasetConfig(
            name=f"multi-bfcl-{code}-public{suffix}",
            pretty_name=f"MultiBFCL-{code}-public",
            source=(
                {"test": str(args.local_csv_dir / f"{code}.csv")}
                if args.local_csv_dir is not None
                else f"{SOURCE}::{code}"
            ),
            task=TOOL_CALLING,
            languages=[LANGUAGES[code]],
            train_split=None,
            val_split=None,
            test_split="test",
            preprocessing_func=partial(
                _preprocess, max_examples=args.max_examples, sample_ids=sample_ids
            ),
            max_generated_tokens=(
                args.max_generated_tokens
                if args.max_generated_tokens is not None
                else 64
                if args.max_examples
                else None
            ),
            # EuroEval's text-to-text ground-truth extractor currently expects
            # cached rows to retain target_text; its bootstrap path does that.
            bootstrap_samples=True,
            unofficial=True,
        )
        for code in languages
    ]
    Benchmarker(
        dataset=configs,
        language=languages,
        few_shot=False,
        evaluate_test_split=True,
        num_iterations=args.num_iterations,
        raise_errors=True,
        api_base=args.api_base,
        generative_type=(
            GenerativeType[args.generative_type.upper()]
            if args.generative_type
            else None
        ),
    ).benchmark(model=args.model)


if __name__ == "__main__":
    main()
