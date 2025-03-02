from langchain_core.language_models import BaseChatModel
from loguru import logger

from llm_string.base import Result
from llm_string.prompts.llm_prompt import get_prompt
from llm_string.prompts.update_prompt import get_update_prompt
from llm_string.string_solvers.base import BaseStringSolver
from llm_string.string_solvers.utils import (generation_with_retry,
                                             value_to_status)
from llm_string.string_validator import (BaseValidator, PythonStringValidator,
                                         StringValidator)
from llm_string.structs import (ConstraintProblem, SolutionStore,
                                ValidatorFeedback)
from llm_string.utils import JSONPydanticOutputParser


class LLMSolverWithFeedback(BaseStringSolver):
    name: str = "llm_with_feedback"
    llm: BaseChatModel
    parser: JSONPydanticOutputParser = JSONPydanticOutputParser(pydantic_object=Result)
    validator: BaseValidator = StringValidator()
    max_retries: int = 5
    use_variable_name: bool = True
    with_explanation: bool = False
    hybrid: bool = False

    def prepare_nl_constraints(self, constraints: list[str], name: str) -> list[str]:
        constraints = "\n".join(constraints)

        if not self.use_variable_name:
            constraints = [
                constraint.replace(name.lower(), "x") for constraint in constraints
            ]
            name = "x"

        return constraints, name

    def transform_counter_examples(
        self, counter_examples: list[ValidatorFeedback]
    ) -> str:
        if not self.with_explanation:
            return "\n".join([f'"{ce.value}"' for ce in counter_examples])
        else:
            samples = []

            for i, ce in enumerate(counter_examples):
                samples.append(
                    f"Counter Example {i}: \"{ce.value}\"\nFailed Constraints:\n{'\n'.join(ce.failed_constraints)}"
                )

            return "\n\n".join(samples)

    def feedback_loop(self, problem: ConstraintProblem) -> str:
        update_chain = get_update_prompt(self.parser) | self.llm
        chain = get_prompt(self.parser) | self.llm

        if self.hybrid:
            logger.info("Using hybrid validation.")
            checker = PythonStringValidator()
            unsat_checker = StringValidator()

        iter_count = 0
        solution_store = SolutionStore()

        while True:
            logger.info(f"current_result: {problem.value}, status {problem.status}")

            if not self.hybrid:
                validation_result = self.validator.validate(problem)
            else:
                if problem.status == "unsat":
                    validation_result = unsat_checker.validate(problem)
                else:
                    validation_result = checker.validate(problem)

            solution_store.add_solution(validation_result)

            if iter_count >= self.max_retries:
                logger.info("Max retries reached.")
                break

            if (
                validation_result.status == "sat"
                or validation_result.status == "unknown"
            ):
                logger.info("Validation successful.")
                break

            logger.info("Validation failed. Retrying...")

            constraints, name = self.prepare_nl_constraints(
                problem.nl_constraints, problem.name
            )
            counter_examples = solution_store.get_counter_examples()
            update_feedback = self.transform_counter_examples(counter_examples)

            logger.info(f"update_feedback:\n{update_feedback}")

            if len(counter_examples) > 0:
                result = generation_with_retry(
                    update_chain,
                    {
                        "name": name,
                        "constraints": constraints,
                        "update_feedback": update_feedback,
                    },
                    self.parser,
                )
            else:
                result = generation_with_retry(
                    chain,
                    {
                        "name": name,
                        "constraints": constraints,
                    },
                    self.parser,
                )
            result, status = value_to_status(result)
            problem.status = status
            problem.value = result

            iter_count += 1

        best_result = solution_store.get_best_solution()
        return best_result.value

    def solve(self, problem: ConstraintProblem) -> ConstraintProblem:
        prompt = get_prompt(self.parser)
        chain = prompt | self.llm
        name = problem.name.strip()

        constraints, name = self.prepare_nl_constraints(problem.nl_constraints, name)
        # logger.info(prompt.format(name=name, constraints=constraints))

        result = generation_with_retry(
            chain,
            {"name": name, "constraints": constraints},
            self.parser,
        )
        result, status = value_to_status(result)
        problem.status = status
        problem.value = result

        result = self.feedback_loop(problem)

        result, status = value_to_status(result)
        problem.status = status
        problem.value = result

        return problem
