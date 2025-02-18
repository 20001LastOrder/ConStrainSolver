import os

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate

from llm_string.constraint_generator.core.examples.examples import get_smt_lib2_example, get_z3py_example

PROMPT_FILE_RELATIVE_PATH = "constraint_generator_prompt.txt"


with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), PROMPT_FILE_RELATIVE_PATH), "r") as f:
    PROMPT_TEXT = f.read()


def get_prompt_template(constraint_type: str, parser: PydanticOutputParser) -> PromptTemplate:
    if constraint_type == "smt-lib2":
        constraint_example_nl, constraint_example_c = get_smt_lib2_example()
    elif constraint_type == "z3py":
        constraint_example_nl, constraint_example_c = get_z3py_example()
    else:
        raise ValueError(f"Unknown constraint type: {constraint_type}. Supported types are: 'smt-lib2', 'z3py'.")

    return PromptTemplate(
        template=PROMPT_TEXT,
        input_variables=["chat_history", "constraint"],
        partial_variables={
            "constraint_type": constraint_type,
            "constraint_example_nl": constraint_example_nl,
            "constraint_example_c": constraint_example_c,
            "output_format": parser.get_format_instructions()
        },
    )