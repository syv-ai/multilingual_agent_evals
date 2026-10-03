"""Run a small MultiIFEval demonstration with local EuroEval dataset configs.

EuroEval is intentionally an optional, separate evaluation dependency. Nothing in
this script modifies EuroEval or starts an evaluation until invoked explicitly.
"""

import argparse
from functools import partial

from datasets import DatasetDict
from euroeval import Benchmarker, DatasetConfig
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
        dataset["test"] = dataset["test"].select(
            range(min(max_examples, len(dataset["test"])))
        )
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
    parser.add_argument("--model", action="append", required=True, help="Hub model ID")
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
    languages = list(dict.fromkeys(args.language or ["da", "en"]))
    configs = [
        DatasetConfig(
            name=f"multi-ifeval-{code}{'-smoke' if args.max_examples else ''}",
            pretty_name=f"MultiIFEval-{code}{'-smoke' if args.max_examples else ''}",
            source=f"{DATASET}::{code}",
            task=INSTRUCTION_FOLLOWING,
            languages=[LANGUAGES[code]],
            preprocessing_func=partial(_preprocess, max_examples=args.max_examples),
            max_generated_tokens=64 if args.max_examples else None,
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
    ).benchmark(model=args.model)


if __name__ == "__main__":
    main()
