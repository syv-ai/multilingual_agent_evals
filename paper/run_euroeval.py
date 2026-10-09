"""Run a small MultiIFEval demonstration with local EuroEval dataset configs.

EuroEval is a project dependency. Nothing in this script modifies EuroEval or
starts an evaluation until invoked explicitly.
"""

import argparse
from functools import partial

from datasets import Dataset, DatasetDict
from euroeval import Benchmarker, DatasetConfig
from euroeval.enums import GenerativeType
from euroeval.languages import DANISH, ENGLISH, FRENCH, GERMAN
from euroeval.tasks import INSTRUCTION_FOLLOWING

LANGUAGES = {"da": DANISH, "en": ENGLISH, "de": GERMAN, "fr": FRENCH}
DATASET = "danish-foundation-models/multi-ifeval"


def _preprocess(dataset: DatasetDict, max_examples: int | None = None) -> DatasetDict:
    """Expose prompt as text and remove Arrow-padded null constraint arguments.

    A normal ``map`` cannot make the nested dictionaries sparse: Arrow reconstructs
    their union schema and fills absent keys with null. A retrieval-time transform
    retains the sparse kwargs expected by EuroEval's instruction checker.

    Args:
        dataset:
            Released, test-only language dataset.
        max_examples (optional):
            Limit the test split for a smoke run. Defaults to None.

    Returns:
        Dataset with a text input column and sparse constraint arguments.
    """
    if max_examples is not None:
        test_split = dataset["test"]
        assert isinstance(test_split, Dataset)
        selected = test_split.select(range(min(max_examples, len(test_split))))
        assert isinstance(selected, Dataset)
        dataset["test"] = selected
    dataset = dataset.map(
        lambda row: {"text": row["prompt"]}, remove_columns=["prompt"]
    )
    return dataset.with_transform(
        lambda batch: {
            **batch,
            "kwargs": [
                [
                    {key: value for key, value in kw.items() if value is not None}
                    for kw in kws
                ]
                for kws in batch["kwargs"]
            ],
        }
    )


def main() -> None:
    """Benchmark the selected models on public, test-only language subsets."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", action="append", required=True, help="Model ID")
    parser.add_argument("--api-base", help="OpenAI-compatible inference API base URL")
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
        help="Language subset; defaults to da and en (repeat to add languages)",
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
    if args.max_generated_tokens is not None and args.max_generated_tokens < 1:
        parser.error("--max-generated-tokens must be positive")
    languages = list(dict.fromkeys(args.language or ["da", "en"]))
    suffix = f"-smoke-{args.max_examples}" if args.max_examples else ""
    configs = [
        DatasetConfig(
            name=f"multi-ifeval-{code}{suffix}",
            pretty_name=f"MultiIFEval-{code}{suffix}",
            source=f"{DATASET}::{code}",
            task=INSTRUCTION_FOLLOWING,
            languages=[LANGUAGES[code]],
            preprocessing_func=partial(_preprocess, max_examples=args.max_examples),
            max_generated_tokens=(
                args.max_generated_tokens
                if args.max_generated_tokens is not None
                else 64
                if args.max_examples
                else None
            ),
            train_split=None,
            val_split=None,
            test_split="test",
            bootstrap_samples=False,
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
        api_base=args.api_base,
        generative_type=(
            GenerativeType[args.generative_type.upper()]
            if args.generative_type
            else None
        ),
    ).benchmark(model=args.model)


if __name__ == "__main__":
    main()
