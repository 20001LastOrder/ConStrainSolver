import os

from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

from llm_string.models import Judgement, Constraint
from llm_string.utils import JSONPydanticOutputParser
from llm_string.logging.logging_overrides import getLogger

PROMPT_FILE_RELATIVE_PATH = "judge_prompt.txt"


with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), PROMPT_FILE_RELATIVE_PATH), "r") as f:
    PROMPT_TEXT = f.read()

logger = getLogger()

class JudgeAgent:
    def __init__(self, constraint_type: str, model_name='gpt-4o-mini', temperature=0.5):
        parser = JSONPydanticOutputParser(pydantic_object=Judgement)

        prompt_template = PromptTemplate(
            template=PROMPT_TEXT,
            input_variables=["nl_constraint", "constraint_c", "example_strings"],
            partial_variables={
                "constraint_type": constraint_type,
                "output_format": parser.get_format_instructions()
            },
        )

        self.chain = prompt_template | ChatOpenAI(model_name=model_name, temperature=temperature) | parser

    def judge(self, nl_constraint: str, constraint_c: Constraint, example_strings: list[dict[str, str]]) -> Judgement | None:
        logger.info("Sending judgement to the LLM: nl_constraint='{0}', constraint_c='{1}', example_strings={2}", nl_constraint, str(constraint_c), str(example_strings))
        try:
            judgement = self.chain.invoke({"nl_constraint": nl_constraint, "constraint_c": str(constraint_c),
                                           "example_strings": str(example_strings)})
        except Exception as e:
            logger.error("Error invoking chain: {0}", str(e))
            return None
        logger.info("Received judgement from the LLM: {0}", str(judgement))
        return judgement