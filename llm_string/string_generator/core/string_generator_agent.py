import os

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

from llm_string.models import SingleVariableExamples, MultiVariableExamples
from llm_string.logging.logging_overrides import getLogger
from llm_string.utils import StringArrayOutputParser

PROMPT_FILE_RELATIVE_PATH = "string_generator_prompt.txt"


with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), PROMPT_FILE_RELATIVE_PATH), "r") as f:
    PROMPT_TEXT = f.read()

logger = getLogger('string_generator_agent')

class StringGeneratorAgent:
    def __init__(self, model_name='gpt-4o-mini', temperature=0.5):
        self.model_name = model_name
        self.temperature = temperature


    def generate_strings(self, constraint: str, number_of_items: int, repetitions=1, variables=None) -> list[list[str]]:
        if variables is None or len(variables) < 1:
            variables = ["string"]

        if len(variables) == 1:
            parser = StringArrayOutputParser()
        else:
            raise NotImplementedError("Only one variable is supported at the moment.")

        prompt_template = PromptTemplate(
            template=PROMPT_TEXT,
            input_variables=["constraint", "variables", "number_of_items", "history"],
            partial_variables={
                "output_format": parser.get_format_instructions()
            },
        )

        chain = prompt_template | ChatOpenAI(model_name=self.model_name, temperature=self.temperature)

        if repetitions < 1:
            logger.error("Repetitions must be at least 1. Returning empty list.")
            return []

        examples = []

        for _ in range(repetitions):
            try:
                logger.info("Sending constraint to the LLM: constraint='%s', number_of_items=%d", constraint, number_of_items)
                llm_response = chain.invoke({"constraint": constraint, "variables": variables, "number_of_items": number_of_items, "history": str(examples)})

                new_examples = parser.parse(llm_response.content)

                if new_examples is None:
                    logger.error("No examples parse from the LLM.")
                    new_examples = []

                logger.info("Received %d items from the LLM: %s", len(new_examples), str(new_examples))
                examples.extend(new_examples)
            except Exception as e:
                logger.error("Error invoking chain: %s", str(e))

        if len(examples) == number_of_items * repetitions:
            logger.info("Received a total of %d items. Returning items.", len(examples))
        else:
            logger.warn("Expected a total of %d items, got %d instead. Proceeding with the items generated.",
                        number_of_items * repetitions, len(examples))

        return examples


# def parse_strings(variables: list[str], items: list[dict[str, str]]) -> list[list[str]]:
#     output = []
#
#     for item in items:
#         parsed_list = []
#         for i in range(len(variables)):
#             variable = variables[i]
#
#             if variable in item:
#                 parsed_list.append(item[variable])
#
#         output.append(parsed_list)
#
#     return output