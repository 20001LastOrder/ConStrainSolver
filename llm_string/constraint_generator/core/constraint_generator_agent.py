from langchain_openai import ChatOpenAI

from llm_string.constraint_generator.core.history_helper import format_history
from llm_string.string_generator.core.string_generator_agent import StringGeneratorAgent
from llm_string.utils import JSONPydanticOutputParser

from llm_string.constraint_generator.core.constraint_evaluator import ConstraintEvaluator
from llm_string.models import Constraint, Judgement
from llm_string.constraint_generator.core.prompt_template_generator import get_prompt_template

from llm_string.logging.logging_overrides import getLogger

logger = getLogger()

class ConstraintGeneratorAgent:
    constraint = None

    def __init__(self, constraint_type: str, model_name='gpt-4o-mini', temperature=0.5):
        parser = JSONPydanticOutputParser(pydantic_object=Constraint)

        prompt_template = get_prompt_template(constraint_type, parser)

        self.chain = prompt_template | ChatOpenAI(model_name=model_name, temperature=temperature) | parser
        self.constraint_type = constraint_type
        self.model_name = model_name
        self.temperature = temperature

    def _get_evaluator(self, constraint_text: str, max_retries=0) -> ConstraintEvaluator | None:
        logger.debug("Received constraint: {0} with max_retries={1}", constraint_text, max_retries)

        attempt = 0

        history = []

        while attempt <= max_retries:
            logger.info("Attempt {0}: sending constraint to the LLM: {1}", attempt + 1, constraint_text)

            history_text = format_history(history)
            logger.debug("Full prompt: {0}", self.chain.steps[0].invoke({"constraint": constraint_text, "history": history_text}))

            try:
                constraint = self.chain.invoke({"constraint": constraint_text, "history": history_text})
            except Exception as e:
                logger.error("Error invoking chain: {0}", str(e))
                attempt += 1
                continue

            logger.info("Received constraint from the LLM: {0}", str(constraint))

            try:
                evaluator = ConstraintEvaluator(self.constraint_type, constraint)

                logger.info("Successfully created evaluator. Returning evaluator.")
                return evaluator
            except Exception as e:
                logger.error("Error creating evaluator for constraint {0}: {1}", constraint, str(e))
                history.append((constraint, e))
                attempt += 1

        logger.error("Failed to create evaluator after {0} attempts. See log for details.", max_retries + 1)

        return None

    def get_evaluator(self, constraint_text: str, max_retries_per_attempt=0, fault_tolerant=True, use_examples=False, use_judge=False, max_steps=10) -> ConstraintEvaluator | None:
        steps = 0
        last_evaluator = None

        while True:
            if steps >= max_steps:
                logger.error("Max steps reached. Returning default value.")
                break

            evaluator = self._get_evaluator(constraint_text, max_retries_per_attempt)
            steps += 1

            if evaluator is None:
                logger.error("Failed to create evaluator. Retry.")
                continue

            if fault_tolerant:
                # if fault-tolerant, the function will return the last valid evaluator even if it failed tests.
                last_evaluator = evaluator

            if use_examples and use_judge:
                judgement = None
                while steps <= max_steps:
                    logger.info("Calling examples generator agent.")
                    failed_examples = self._execute_examples_step(constraint_text, evaluator, max_retries_per_attempt)
                    steps += 1

                    if len(failed_examples) == 0:
                        logger.info("Evaluator passed all examples.")
                        break

                    logger.error("Evaluator failed examples: {0}.", failed_examples)

                    logger.info("Calling judge agent.")
                    judgement = self._execute_judge_step()
                    steps += 1

                    if judgement is not None and not judgement.example_strings_are_correct:
                        logger.error("Error attributed to examples by judge. Regenerate examples.")
                        continue

                    break

                if judgement is not None and not judgement.evaluator_expression_is_correct:
                    logger.error("Error attributed to evaluator by judge. Retry.")
                    continue

            elif use_examples:
                logger.info("Calling examples generator agent.")
                failed_examples = self._execute_examples_step(constraint_text, evaluator, max_retries_per_attempt)
                steps += 1

                if len(failed_examples) > 0:
                    logger.error("Evaluator failed examples: {0}. Retry", failed_examples)

                    continue
                else:
                    logger.info("Evaluator passed all examples.")

            logger.info("Evaluator passed all checks. Returning evaluator.")
            return evaluator

        return last_evaluator


    def _execute_examples_step(self, constraint_text: str, evaluator: ConstraintEvaluator, max_retries: int) -> list[list[str]]:
        string_generator_agent = StringGeneratorAgent(self.model_name, self.temperature)

        try:
            example_strings = string_generator_agent.generate_strings_with_retries(
                constraint_text,
                variables=evaluator.constraint.variables,
                number_of_items=10,
                max_retries=max_retries
            )
        except Exception as e:
            logger.error("Error generating example strings: {0}", str(e))
            return []

        failed_examples = []

        for example in example_strings:
            if not evaluator.safe_evaluate(*example):
                failed_examples.append(example)

        return failed_examples


    def _execute_judge_step(self) -> Judgement:
        pass
