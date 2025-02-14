from typing import Literal

from pydantic import BaseModel

from llm_string.string_solvers import Z3Solver
from llm_string.string_solvers.base import ConstraintProblem


class StringValidator(BaseModel):
    solver: Z3Solver = Z3Solver(solver_name="z3")

    def validate(
        self,
        status: Literal["sat", "unsat", "unknown"],
        constraints: list[str],
        solution: str,
    ) -> Literal["sat", "unsat", "unknown"]:

        if status != "UNSAT":
            constraints = ['(assert (= s "' + solution + '"))'] + constraints

        problem = ConstraintProblem(smt_constraints=constraints, name="validate")
        problem = self.solver.solve(problem)

        return problem.status
