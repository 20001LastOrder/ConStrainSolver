from langchain_openai import ChatOpenAI

from llm_string.constraint_generator.core.history_helper import format_history
from llm_string.utils import JSONPydanticOutputParser

from llm_string.constraint_generator.core.constraint_evaluator import ConstraintEvaluator
from llm_string.constraint_generator.core.model import Constraint
from llm_string.constraint_generator.core.prompt_template_generator import get_prompt_template

import llm_string.constraint_generator.utils.logging_overrides as logging

logger = logging.getLogger('llmagent')

class LLMAgent:
    constraint = None

    def __init__(self, constraint_type: str, model_name='gpt-4o-mini', temperature=0.5):
        parser = JSONPydanticOutputParser(pydantic_object=Constraint)

        prompt_template = get_prompt_template(constraint_type, parser)

        self.chain = prompt_template | ChatOpenAI(model_name=model_name, temperature=temperature) | parser
        self.constraint_type = constraint_type

    def get_evaluator(self,  constraint_text: str, max_retries=0) -> ConstraintEvaluator | None:
        logger.debug("Received constraint: %s with max_retries=%d", constraint_text, max_retries)

        attempt = 0

        history = []

        while attempt <= max_retries:
            logger.info("Attempt %d: sending constraint to the LLM: %s", attempt + 1, constraint_text)

            history_text = format_history(history)
            logger.debug("Full prompt: %s", self.chain.steps[0].invoke({"constraint": constraint_text, "history": history_text}))

            try:
                constraint = self.chain.invoke({"constraint": constraint_text, "history": history_text})
            except Exception as e:
                logger.error("Error invoking chain: %s", str(e))
                attempt += 1
                continue

            logger.info(f"Received constraint from the LLM: %s", str(constraint))

            try:
                evaluator = ConstraintEvaluator(self.constraint_type, constraint)

                logger.info("Successfully created evaluator. Returning evaluator.")
                return evaluator
            except Exception as e:
                logger.error("Error creating evaluator for constraint %s: %s", constraint, str(e))
                history.append((constraint, e))
                attempt += 1

        logger.error("Failed to create evaluator after %d attempts. See log for details.", max_retries + 1)

        return None