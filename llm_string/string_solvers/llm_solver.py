from langchain_core.language_models import BaseChatModel

from llm_string.prompts.llm_prompt import get_prompt
from llm_string.string_solvers.base import BaseStringSolver, ConstraintProblem
from llm_string.utils import JSONPydanticOutputParser


class LLMSolver(BaseStringSolver):
    llm: BaseChatModel
    parser: JSONPydanticOutputParser = JSONPydanticOutputParser()
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

        while True:
            result = chain.invoke(input={"name": name, "constraints": constraints})
            try:
                result = self.parser.parse(result.content).value
                break
            except ValueError:
                continue

        if result.lower() != "UNSAT":
            problem.status = "sat"
            problem.value = result
        else:
            problem.status = "unsat"
        return problem
