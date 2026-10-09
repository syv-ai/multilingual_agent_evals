"""Benchmark the public MultiBFCL release with a local EuroEval dataset config.

This does not change EuroEval or rely on its possibly private derived mini datasets.
Model inference starts only when the script is invoked with a model ID.
"""

import argparse
import json
from functools import partial

from datasets import Dataset, DatasetDict
from euroeval import Benchmarker, DatasetConfig
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


def _preprocess(dataset: DatasetDict, max_examples: int | None = None) -> DatasetDict:
    """Convert the public test split, optionally limiting a smoke run.

    Args:
        dataset:
            The released language subset with only a test split.
        max_examples (optional):
            Number of examples for a smoke run. Defaults to None.

    Returns:
        A test-only dataset in EuroEval's tool-calling format.
    """
    test_split = dataset["test"]
    assert isinstance(test_split, Dataset)
    if max_examples is not None:
        selected = test_split.select(range(min(max_examples, len(test_split))))
        assert isinstance(selected, Dataset)
        test_split = selected
    converted = test_split.map(_convert_row, remove_columns=test_split.column_names)
    assert isinstance(converted, Dataset)
    return DatasetDict({"test": converted})


def main() -> None:
    """Run separate tool-calling scores for the selected models and languages."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", action="append", required=True, help="Hub model ID")
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
    args = parser.parse_args()
    if args.max_examples is not None and args.max_examples < 1:
        parser.error("--max-examples must be positive")
    languages = list(dict.fromkeys(args.language or ["da"]))
    configs = [
        DatasetConfig(
            name=f"multi-bfcl-{code}-public{'-smoke' if args.max_examples else ''}",
            pretty_name=f"MultiBFCL-{code}-public",
            source=f"{SOURCE}::{code}",
            task=TOOL_CALLING,
            languages=[LANGUAGES[code]],
            train_split=None,
            val_split=None,
            test_split="test",
            preprocessing_func=partial(_preprocess, max_examples=args.max_examples),
            max_generated_tokens=64 if args.max_examples else None,
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
        num_iterations=1,
        raise_errors=True,
    ).benchmark(model=args.model)


if __name__ == "__main__":
    main()
