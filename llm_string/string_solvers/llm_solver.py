from langchain_core.language_models import BaseChatModel

from llm_string.base import Result
from llm_string.prompts.llm_prompt import get_prompt
from llm_string.string_solvers.base import BaseStringSolver
from llm_string.string_solvers.utils import generation_with_retry
from llm_string.structs import ConstraintProblem
from llm_string.utils import JSONPydanticOutputParser


class LLMSolver(BaseStringSolver):
    name: str = "llm"
    llm: BaseChatModel
    parser: JSONPydanticOutputParser = JSONPydanticOutputParser(pydantic_object=Result)
    use_variable_name: bool = True

    def solve(self, problem: ConstraintProblem) -> ConstraintProblem:
        prompt = get_prompt(self.parser)
        chain = prompt | self.llm
        name = problem.name.strip()
        constraints = "\n".join(problem.nl_constraints)

        if not self.use_variable_name:
            constraints = [
                constraint.replace(name.lower(), "x") for constraint in constraints
            ]
            name = "x"

        result = generation_with_retry(
            chain, {"name": name, "constraints": constraints}
        )

        if result.lower() != "unsat":
            problem.status = "sat"
            problem.value = result
        else:
            problem.status = "unsat"
        return problem
