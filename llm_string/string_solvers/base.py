from abc import ABC, abstractmethod
from typing import Callable, Literal

from pydantic import BaseModel


class ConstraintProblem(BaseModel):
    nl_constraints: list[str] = []
    smt_constraints: list[str] = []
    python_checkers: list[Callable] = []
    name: str
    status: Literal["sat", "unsat", "unknown"] = "unknown"
    value: str = ""


class BaseStringSolver(BaseModel, ABC):
    name: str = ""

    @abstractmethod
    def solve(self, problem: ConstraintProblem) -> ConstraintProblem:
        pass
