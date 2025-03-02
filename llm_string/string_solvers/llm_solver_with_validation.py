from langchain_core.language_models import BaseChatModel
from loguru import logger

from llm_string.base import Result
from llm_string.prompts.llm_prompt import get_prompt
from llm_string.string_solvers.base import BaseStringSolver
from llm_string.string_solvers.utils import (generation_with_retry,
                                             value_to_status)
from llm_string.string_validator import (BaseValidator, PythonStringValidator,
                                         StringValidator)
from llm_string.structs import ConstraintProblem, SolutionStore
from llm_string.utils import JSONPydanticOutputParser


class LLMSolverWithValidation(BaseStringSolver):
    name: str = "llm_with_validation"
    llm: BaseChatModel
    parser: JSONPydanticOutputParser = JSONPydanticOutputParser(pydantic_object=Result)
    validator: BaseValidator = StringValidator()
    max_retries: int = 5
    use_variable_name: bool = True
    hybrid: bool = False

    def prepare_nl_constraints(self, constraints: list[str], name: str) -> list[str]:
        constraints = "\n".join(constraints)

        if not self.use_variable_name:
            constraints = [
                constraint.replace(name.lower(), "x") for constraint in constraints
            ]
            name = "x"

        return constraints, name

    def feedback_loop(self, problem: ConstraintProblem) -> str:
        prompt = get_prompt(self.parser)
        chain = prompt | self.llm
        iter_count = 0
        solution_store = SolutionStore()

        if self.hybrid:
            logger.info("Using hybrid validation.")
            checker = PythonStringValidator()
            unsat_checker = StringValidator()

        while iter_count < self.max_retries:
            logger.info(f"current_result: {problem.value}, status {problem.status}")
            if not self.hybrid:
                validation_result = self.validator.validate(problem)
            else:
                if problem.status == "unsat":
                    validation_result = unsat_checker.validate(problem)
                else:
                    validation_result = checker.validate(problem)
            solution_store.add_solution(validation_result)

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

            # logger.info(prompt.format(name=name, constraints=constraints))
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
