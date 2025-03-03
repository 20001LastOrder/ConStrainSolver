from langchain.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

PROMPT_TEXT = """You are a test engineer working on creating test data for a new feature. You are given a variable "{name}" with some associated constraints.

First, explain the meaning of each constraint. Then think step by step to find a string value for "{name}" that satisfy ALL following constraints:
{constraints}
The value should be as realistic for "{name}" as possible.

The output should follow the following format. If no value can satisfy all constraints, assign the value "UNSAT":
{output_format}
Makesure to surround the final output with:
```json
```

Keep the results concise. If the answer is not correct, then you will be fired from your job.
"""  # noqa: E501


def get_prompt(parser: PydanticOutputParser) -> ChatPromptTemplate:
    return ChatPromptTemplate(
        messages=[("user", PROMPT_TEXT)],
        input_variables=["name", "constraints"],
        partial_variables={"output_format": parser.get_format_instructions()},
    )
