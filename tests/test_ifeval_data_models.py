"""Tests for the `multi_ifeval.data_models` module."""

from multi_ifeval.data_models import GeneratedExample, Kwarg


def test_generated_example_filters_empty_kwargs() -> None:
    """Empty-string and empty-list kwargs are dropped, other values are kept.

    `model_post_init` used to test membership against the set literal `{"", []}`.
    Building that set raises `TypeError: unhashable type: 'list'` as soon as any
    kwarg is checked, so every translated example with keyword arguments failed
    validation and was skipped.
    """
    example = GeneratedExample(
        new_prompt="some prompt",
        new_instruction_id_list=["keywords:existence", "punctuation:no_comma"],
        new_kwargs=[
            [
                Kwarg(name="keywords", value=["alpha", "beta"]),
                Kwarg(name="extra", value=[]),
            ],
            [Kwarg(name="blank", value="")],
        ],
    )
    assert example.new_kwargs == [[Kwarg(name="keywords", value=["alpha", "beta"])], []]


def test_generated_example_keeps_false_and_zero_kwargs() -> None:
    """Kwargs with a `False` or `0` value are kept."""
    example = GeneratedExample(
        new_prompt="some prompt",
        new_instruction_id_list=["length_constraints:number_words"],
        new_kwargs=[
            [Kwarg(name="num_words", value=0), Kwarg(name="capital", value=False)]
        ],
    )
    assert example.new_kwargs == [
        [Kwarg(name="num_words", value=0), Kwarg(name="capital", value=False)]
    ]
