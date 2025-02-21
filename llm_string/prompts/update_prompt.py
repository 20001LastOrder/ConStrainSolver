from langchain.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

PROMPT_TEXT = """You are a test engineer working on creating test data for a new feature. You are given a variable "{name}" with some associated constraints.

Your target is to find a string value for "{name}" that satisfy ALL following constraints:
{constraints}
If the word "{name}" is meaningful, the value should be as realistic for "{name}" as possible.

One of your team members has already tried to solve this problem with the following string values:
{previous_values}

However, this value does not satisfy all constraints. Your task is to find a new string value that satisfies all constraints.

The output should follow the following format. If no value can satisfy all constraints, assign the value "UNSAT":
{output_format}

Keep the results concise. If the answer is not correct, then you will be fired from your job.
"""  # noqa: E501


def get_update_prompt(parser: PydanticOutputParser) -> ChatPromptTemplate:
    return ChatPromptTemplate(
        messages=[("user", PROMPT_TEXT)],
        input_variables=["name", "constraints", "previous values"],
        partial_variables={"output_format": parser.get_format_instructions()},
    )
