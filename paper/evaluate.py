"""Run a small MultiIFEval demonstration with local EuroEval dataset configs.

EuroEval is intentionally an optional, separate evaluation dependency. Nothing in
this script modifies EuroEval or starts an evaluation until invoked explicitly.
"""

import argparse

from datasets import DatasetDict
from euroeval import Benchmarker, DatasetConfig
from euroeval.languages import DANISH, ENGLISH, FRENCH, GERMAN
from euroeval.tasks import INSTRUCTION_FOLLOWING

LANGUAGES = {"da": DANISH, "en": ENGLISH, "de": GERMAN, "fr": FRENCH}
DATASET = "danish-foundation-models/multi-ifeval"


def _preprocess(dataset: DatasetDict) -> DatasetDict:
    """Expose prompt as text and remove Arrow-padded null constraint arguments.

    A normal ``map`` cannot make the nested dictionaries sparse: Arrow reconstructs
    their union schema and fills absent keys with null. A retrieval-time transform
    retains the sparse kwargs expected by EuroEval's instruction checker.

    Args:
        dataset:
            Released, test-only language dataset.

    Returns:
        Dataset with a text input column and sparse constraint arguments.
    """
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
    args = parser.parse_args()
    languages = list(dict.fromkeys(args.language or ["da", "en"]))
    configs = [
        DatasetConfig(
            name=f"multi-ifeval-{code}",
            pretty_name=f"MultiIFEval-{code}",
            source=f"{DATASET}::{code}",
            task=INSTRUCTION_FOLLOWING,
            languages=[LANGUAGES[code]],
            train_split=None,
            val_split=None,
            test_split="test",
            preprocessing_func=_preprocess,
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
