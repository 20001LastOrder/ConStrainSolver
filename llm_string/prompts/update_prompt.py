from langchain.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

PROMPT_TEXT = """You are a test engineer working on creating test data for a new feature. You are given a variable "{name}" with some associated constraints.

Your target is to find a string value for "{name}" that satisfies ALL of the following constraints:
{constraints}
If the word "{name}" is meaningful, the value should be as realistic as possible.

Before proposing a candidate value, analyze whether the constraints are logically consistent. If any constraints conflict, explain which ones and conclude that no value can satisfy all constraints (output "UNSAT").

Below are previously generated values for "{name}" provided as counter examples in the following format: "<value>". Note that these values do not satisfy all constraints:
{update_feedback}

Your output should follow the format below. If no value can satisfy all constraints, assign the value "UNSAT":
{output_format}

Please follow these steps:
1. **Summarize Counter Example Violations:** For each counter example, describe how it fails to meet the constraints.
2. **Analyze the Constraints:** Evaluate each constraint individually and together. If you detect any logical contradiction or ambiguity (for example, a constraint that requires the string to start with a space and another that requires the first character to be capitalized), explain the conflict.
3. **Determine Feasibility:**
   - If it is possible to find a valid value, provide the new value and explain how it satisfies every constraint.
   - If not, explain why no valid value exists and output "UNSAT".
"""  # noqa: E501


def get_update_prompt(parser: PydanticOutputParser) -> ChatPromptTemplate:
    return ChatPromptTemplate(
        messages=[("user", PROMPT_TEXT)],
        input_variables=["name", "constraints", "previous values"],
        partial_variables={"output_format": parser.get_format_instructions()},
    )
