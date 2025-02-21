from typing import Literal

from pydantic import BaseModel

from llm_string.string_solvers import Z3Solver
from llm_string.string_solvers.base import ConstraintProblem


class StringValidator(BaseModel):
    timeout: int = 10000
    solver: Z3Solver = Z3Solver(solver_name="z3", timeout=timeout)

    def validate(
        self,
        status: Literal["sat", "unsat", "unknown"],
        constraints: list[str],
        solution: str = "",
    ) -> Literal["sat", "unsat", "unknown"]:
        """
        Validate the solution of constraints if the status is SAT

        Args:
            status (Literal["sat", "unsat", "unknown"]): The status of the problem
            constraints (list[str]): The constraints to validate
            solution (str, optional): The solution to validate. Defaults to "". Must be
                provided if status is not "UNSAT".

        Returns:
            Literal["sat", "unsat", "unknown"]: The status of the validation
        """

        if status == "sat":
            constraints = ['(assert (= s "' + solution + '"))'] + constraints

        problem = ConstraintProblem(smt_constraints=constraints, name="validate")
        problem = self.solver.solve(problem)

        return problem.status
