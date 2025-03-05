import os
import re

from langchain_core.prompts import PromptTemplate

from llm_string.models import Constraint

HISTORY_PROMPT_FILE_RELATIVE_PATH = "constraint_generator_history_prompt.txt"

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), HISTORY_PROMPT_FILE_RELATIVE_PATH), "r") as f:
    HISTORY_PROMPT_TEXT = f.read()

def format_history(history: list[(Constraint, Exception)]) -> str:
    if not history:
        return ""

    errors = "\n".join([f"Constraint {{\"variables\": {str(h[0].variables)}, \"constraint\": \"{h[0].constraint}\"}} is incorrect for this reason: {format_exception(h[0].constraint, h[1])}" for i, h in enumerate(history)])

    return PromptTemplate(
        template=HISTORY_PROMPT_TEXT,
        input_variables=["constraints_count", "errors"],
    ).format(constraints_count=len(history), errors=errors)


def format_exception(constraint: str, ex: Exception) -> str:
    exception_string = str(ex)

    pattern = r"\"line 1 column (\d+):"
    return re.sub(pattern, lambda m: f"near \"{constraint[max(int(m.group(1)) - 35, 0):min(int(m.group(1)) - 20, len(constraint) - 1)]}\":", exception_string)