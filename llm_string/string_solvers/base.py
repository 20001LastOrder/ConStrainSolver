from abc import ABC, abstractmethod

from pydantic import BaseModel

from llm_string.structs import ConstraintProblem


class BaseStringSolver(BaseModel, ABC):
    name: str = ""

    @abstractmethod
    def solve(self, problem: ConstraintProblem) -> ConstraintProblem:
        pass
