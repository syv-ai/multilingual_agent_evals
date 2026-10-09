"""Translation of tool calling examples."""

from copy import deepcopy
from textwrap import dedent

from .data_models import Example, TranslationOutput
from .languages import Language
from .llm import generate


def translate_example(
    example: Example,
    language: Language,
    language_example: str,
    model: str,
    api_base: str,
) -> Example:
    """Translate a tool calling example to a different language.

    Args:
        example:
            The example to translate.
        language:
            The language code to translate the example to.
        language_example:
            An example of some text written in the target language.
        model:
            The model to use for translation.
        api_base:
            The base URL for the API.

    Returns:
        The translated example.
    """
    new_example = deepcopy(example)

    prompt = dedent(f"""
        You are a professional translator from English to {language.name} (language
        code: {language.code!r}).

        Here is an example of some text written in {language.name}:

        <{language.code}-example>
        {language_example.replace("\n", " ")}
        </{language.code}-example>

        Here is an instruction in English:

        <example>
        {{instruction}}
        </example>

        You need to translate the instruction to {language.name}.

        You should return the translated instruction in JSON format, with the following
        structure:

        - `new_instruction` (str): The translated instruction.
    """).strip()

    system_or_user_prompt = example.question[0][0]["content"]
    generated_example = generate(
        prompt=prompt.format(instruction=system_or_user_prompt),
        model=model,
        api_base=api_base,
        temperature=0.0,
        response_format=TranslationOutput,
    )
    new_example.question[0][0]["content"] = generated_example.new_instruction

    # If the first message is a system message, then we also need to translate the user
    # message
    if example.question[0][0]["role"] == "system":
        user_prompt = example.question[0][1]["content"]
        generated_example = generate(
            prompt=prompt.format(instruction=user_prompt),
            model=model,
            api_base=api_base,
            temperature=0.0,
            response_format=TranslationOutput,
        )
        new_example.question[0][1]["content"] = generated_example.new_instruction

    return new_example
