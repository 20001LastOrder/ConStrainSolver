import re
from abc import ABC, abstractmethod

from loguru import logger
from pydantic import BaseModel

from llm_string.string_solvers.base import BaseStringSolver, ConstraintProblem
from llm_string.string_solvers.formal_solvers import CVC5Solver
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
    produce_failed_constraints: bool = False
    solver: BaseStringSolver = CVC5Solver(solver_name="z3", timeout=timeout)

    def get_failed_constraints(self, original_problem: ConstraintProblem) -> list[str]:
        solution = original_problem.value
        failed_constraints = []

        for i, constraint in enumerate(original_problem.smt_constraints):
            constraints = ['(assert (= s "' + solution + '"))', constraint]
            problem = ConstraintProblem(smt_constraints=constraints, name="validate")
            problem = self.solver.solve(problem)
            if problem.status == "unsat":
                failed_constraints.append(original_problem.nl_constraints[i])

        return failed_constraints

    def validate(
        self,
        original_problem: ConstraintProblem,
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
        initial_status = original_problem.status
        constraints = original_problem.smt_constraints
        solution = original_problem.value

        if initial_status == "sat":
            constraints = ['(assert (= s "' + solution + '"))'] + constraints

        problem = ConstraintProblem(smt_constraints=constraints, name="validate")

        failed_constraints = []
        problem = self.solver.solve(problem)

        if problem.status == "unknown":
            return ValidatorFeedback(status="unknown", message="")

        failed_constraints = []
        if (
            problem.status == "unsat"
            and initial_status == "sat"
            and self.produce_failed_constraints
        ):
            failed_constraints = self.get_failed_constraints(original_problem)

        if problem.status != initial_status:
            status = "unsat"
        else:
            status = "sat"

        logger.info(
            f"The input problem status is {initial_status} and the validation status is {status}"
        )
        return ValidatorFeedback(
            value=solution, status=status, failed_constraints=failed_constraints
        )


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
