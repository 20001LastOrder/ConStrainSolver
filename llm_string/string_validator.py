from abc import ABC, abstractmethod

from loguru import logger
from pydantic import BaseModel

from llm_string.string_solvers import Z3Solver
from llm_string.string_solvers.base import ConstraintProblem
from llm_string.structs import ValidatorFeedback


class BaseValidator(BaseModel, ABC):
    @abstractmethod
    def validate(
        self,
        problem: ConstraintProblem,
    ) -> ValidatorFeedback:
        pass


class StringValidator(BaseValidator):
    timeout: int = 10000
    solver: Z3Solver = Z3Solver(solver_name="z3", timeout=timeout)

    def validate(
        self,
        problem: ConstraintProblem,
    ) -> ValidatorFeedback:
        """
        Validate the solution of constraints if the status is SAT

        Args:
            status (Literal["sat", "unsat", "unknown"]): The status of the problem
            constraints (list[str]): The constraints to validate
            solution (str, optional): The solution to validate. Defaults to "". Must be
                provided if status is not "UNSAT".

        Returns:
            ValidatorFeedback: The validator output
        """
        status = problem.status
        constraints = problem.smt_constraints
        solution = problem.value

        if status == "sat":
            constraints = ['(assert (= s "' + solution + '"))'] + constraints


        problem = ConstraintProblem(smt_constraints=constraints, name="validate")
        problem = self.solver.solve(problem)

        # TODO: add unsat core
        return ValidatorFeedback(status=problem.status, message="")


class PythonStringValidator(BaseValidator):
    def validate(
        self,
        problem: ConstraintProblem,
    ):
        if problem.status == "unsat" or problem.status == "unknown":
            return ValidatorFeedback(value="", status="unknown")

        checkers = problem.python_checkers
        solution = problem.value

        unsat_constraints = []
        for i, checker in enumerate(checkers):
            if not checker(solution):
                unsat_constraints.append(problem.nl_constraints[i])

        if len(unsat_constraints) == 0:
            return ValidatorFeedback(value=solution, status="sat")
        else:
            return ValidatorFeedback(
                value=solution, status="unsat", failed_constraints=unsat_constraints
            )
