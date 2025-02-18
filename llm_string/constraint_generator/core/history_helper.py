import os

from langchain_core.prompts import PromptTemplate

from llm_string.constraint_generator.core.model import Constraint

HISTORY_PROMPT_FILE_RELATIVE_PATH = "constraint_generator_history_prompt.txt"

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), HISTORY_PROMPT_FILE_RELATIVE_PATH), "r") as f:
    HISTORY_PROMPT_TEXT = f.read()

def format_history(history: list[(Constraint, Exception)]) -> str:
    if not history:
        return ""

    errors = "\n".join([f"Constraint {{\"variables\": {str(h[0].variables)}, \"constraint\": \"{h[0].constraint}\"}} is incorrect for this reason: {h[1]}" for i, h in enumerate(history)])

    return PromptTemplate(
        template=HISTORY_PROMPT_TEXT,
        input_variables=["constraints_count", "errors"],
    ).format(constraints_count=len(history), errors=errors)