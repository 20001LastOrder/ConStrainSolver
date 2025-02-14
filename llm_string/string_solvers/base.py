from abc import ABC, abstractmethod
from typing import Literal

from pydantic import BaseModel


class ConstraintProblem(BaseModel):
    nl_constraints: list[str] = []
    smt_constraints: list[str] = []
    name: str
    status: Literal["sat", "unsat", "unknown"] = "unknown"
    value: str = ""


class BaseStringSolver(BaseModel, ABC):
    @abstractmethod
    def solve(self, problem: ConstraintProblem) -> ConstraintProblem:
        pass
