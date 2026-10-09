"""Checks for the local public-data EuroEval conversion."""

import pytest
from datasets import Dataset, DatasetDict

from paper.run_multibfcl import _preprocess


def test_selects_matched_source_ids_in_requested_order() -> None:
    """Preserve IDs and order when preparing a parallel-language sample."""
    rows = [
        {
            "id": source_id,
            "question": f'[[{{"role": "user", "content": "Question {source_id}"}}]]',
            "function": "[]",
            "ground_truth": "[]",
        }
        for source_id in ("live_1", "simple_2")
    ]
    converted = _preprocess(
        dataset=DatasetDict({"test": Dataset.from_list(rows)}),
        sample_ids=["simple_2", "live_1"],
    )
    assert converted["test"]["id"] == ["simple_2", "live_1"]
    assert converted["test"]["text"][0] == "Functions:\n[]\nQuestion: Question simple_2"
    assert converted["test"]["target_text"] == ["[]", "[]"]


def test_rejects_missing_source_ids() -> None:
    """Never silently compare different records across languages."""
    dataset = DatasetDict(
        {
            "test": Dataset.from_list(
                [
                    {
                        "id": "live_1",
                        "question": '[[{"role": "user", "content": "Hi"}]]',
                        "function": "[]",
                        "ground_truth": "[]",
                    }
                ]
            )
        }
    )
    with pytest.raises(ValueError, match="missing_id"):
        _preprocess(dataset=dataset, sample_ids=["missing_id"])
