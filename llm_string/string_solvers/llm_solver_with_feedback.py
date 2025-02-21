from langchain_core.language_models import BaseChatModel
from loguru import logger

from llm_string.base import Result
from llm_string.prompts.llm_prompt import get_prompt
from llm_string.prompts.update_prompt import get_update_prompt
from llm_string.string_solvers.base import BaseStringSolver, ConstraintProblem
from llm_string.string_solvers.utils import generation_with_retry
from llm_string.string_validator import StringValidator
from llm_string.utils import JSONPydanticOutputParser


class LLMSolverWithFeedback(BaseStringSolver):
    name: str = "llm_with_feedback"
    llm: BaseChatModel
    parser: JSONPydanticOutputParser = JSONPydanticOutputParser(pydantic_object=Result)
    validator: StringValidator = StringValidator()
    max_retries: int = 5
    use_variable_name: bool = True

    def prepare_nl_constraints(self, constraints: list[str], name: str) -> list[str]:
        constraints = "\n".join(constraints)

        if not self.use_variable_name:
            constraints = [
                constraint.replace(name.lower(), "x") for constraint in constraints
            ]
            name = "x"

        return constraints, name

    def feedback_loop(
        self,
        nl_constraints: list[str],
        formal_constraints: list[str],
        name: str,
        initial_result: str,
    ) -> str:
        update_chain = get_update_prompt(self.parser) | self.llm
        iter_count = 0
        previous_values = []
        result = initial_result

        while iter_count < self.max_retries:
            logger.info(f"current_result: {result}")
            if result.lower() == "unsat":
                result = ""

            validation_status = self.validator.validate(
                "sat" if result != "" else "unsat", formal_constraints, result
            )

            if (validation_status == "sat" and result != "") or (
                validation_status == "unsat" and result == ""
            ):
                logger.info("Validation successful.")
                break

            logger.info("Validation failed. Retrying...")

            previous_values.append(result)
            result = generation_with_retry(
                update_chain,
                {
                    "name": name,
                    "constraints": nl_constraints,
                    "previous_values": "\n".join(previous_values),
                },
                self.parser,
            )

            iter_count += 1

        return "unsat" if result == "" else result

    def solve(self, problem: ConstraintProblem) -> ConstraintProblem:
        prompt = get_prompt(self.parser)
        chain = prompt | self.llm
        name = problem.name.strip()

        constraints, name = self.prepare_nl_constraints(problem.nl_constraints, name)

        result = generation_with_retry(
            chain,
            {"name": name, "constraints": constraints},
            self.parser,
        )

        result = self.feedback_loop(constraints, problem.smt_constraints, name, result)

        if result.lower() != "unsat":
            problem.status = "sat"
            problem.value = result
        else:
            problem.status = "unsat"
        return problem
