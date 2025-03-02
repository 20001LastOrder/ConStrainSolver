import ast
import inspect
from typing import Callable, Literal

from loguru import logger
from pydantic import BaseModel, Field
from pydantic.dataclasses import dataclass

from llm_string.utils import source_code_to_function


def negate_function(func):
    def negated_func(*args, **kwargs):
        return not func(*args, **kwargs)

    return negated_func


class ConstraintProblem(BaseModel):
    nl_constraints: list[str] = []
    smt_constraints: list[str] = []
    truth_masks: list[bool] = []
    python_programs: list[str] = []

    name: str
    status: Literal["sat", "unsat", "unknown"] = "unknown"
    value: str = ""

    @property
    def python_checkers(self) -> list[Callable]:
        if len(self.truth_masks) == 0:
            truth_masks = [True] * len(self.nl_constraints)
        else:
            truth_masks = self.truth_masks

        results = []
        for i, mask in enumerate(truth_masks):
            func = source_code_to_function(self.python_programs[i])
            if mask:
                results.append(func)
            else:
                results.append(negate_function(func))

        return results


@dataclass
class ValidatorFeedback:
    value: str = ""
    status: Literal["sat", "unsat", "unknown"] = "unknown"
    failed_constraints: list[str] = Field(default_factory=list)


class SolutionStore(BaseModel):
    solutions: list[ValidatorFeedback] = []

    def add_solution(self, solution: ValidatorFeedback):
        self.solutions.append(solution)

    def get_best_solution(self) -> ValidatorFeedback:
        for solution in self.solutions:
            if solution.status == "sat":
                return solution

        unsat_count_proposals = []
        sat_proposals = []
        for solution in self.solutions:
            if solution.value != "" and solution.status != "unsat":
                sat_proposals.append(solution)
            else:
                unsat_count_proposals.append(solution)

        if len(unsat_count_proposals) > len(sat_proposals):
            return unsat_count_proposals[0]
        else:
            return min(sat_proposals, key=lambda x: len(x.failed_constraints))

    def get_counter_examples(self) -> list[ValidatorFeedback]:
        counter_examples = [
            solution for solution in self.solutions if solution.status == "unsat"
        ]

        results = []
        for example in counter_examples:
            logger.info(example.value)
            if example.value != "":
                results.append(example)
        return results
