import json
from typing import Callable

import pandas as pd
from loguru import logger

from llm_string.string_solvers.base import ConstraintProblem


class ConstraintStore:
    file_path: str

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.df = pd.read_csv(file_path, encoding="utf-8", index_col="Name")
        self.df.fillna("", inplace=True)

        self.df["NL description"] = self.df["NL description"].apply(
            lambda x: x.replace("\r", "").split("\n\n")
        )
        self.df["NL negation"] = self.df["NL negation"].apply(
            lambda x: x.replace("\r", "").split("\n\n")
        )
        self.df["SMT-LIB2"] = self.df["SMT-LIB2"].apply(
            lambda x: x.replace("\r", "").split("\n\n")
        )
        self.df["SMT-LIB2 negation"] = self.df["SMT-LIB2 negation"].apply(
            lambda x: x.replace("\r", "").split("\n\n")
        )

        self.df["Functions"] = self.df["Functions"].astype(object).apply(
            lambda x: json.loads(x)
        )

    def get_constraint_names(self) -> list[str]:
        return self.df.index.tolist()

    def get_num_constraints(self, name: str) -> int:
        return len(self.df.loc[name, "NL description"])

    def get_nl_constraints(self, name: str, truth_masks: list[bool]) -> list[str]:
        """
        Get the natural language description of the constraints for a given name.
        truth_masks is a list of boolean values that indicate whether the original
        constraint is used or its negation is used.

        Args:
            name (str): The name of the constraint.
            truth_masks (list[bool]): A list of boolean values that indicate whether
                the original constraint is used or its negation is used.

        Returns:
            list[str]: A list of natural language descriptions of the constraints.
        """
        results = []
        for i, mask in enumerate(truth_masks):
            if mask:
                results.append(self.df.loc[name, "NL description"][i])
            else:
                results.append(self.df.loc[name, "NL negation"][i])
        return results

    def get_smt_constraints(self, name: str, truth_masks: list[bool]) -> list[str]:
        """

        Get the SMT-LIB2 representation of the constraints for a given name.
        truth_masks is a list of boolean values that indicate whether the original
        constraint is used or its negation is used.

        Args:
            name (str): The name of the constraint.
            truth_masks (list[bool]): A list of boolean values that indicate whether
                the original constraint is used or its negation is used.

        Returns:
            list[str]: A list of SMT-LIB2 representation of the constraints.
        """
        if len(self.df.loc[name, "SMT-LIB2"]) != len(truth_masks):
            logger.warning(
                f"Number of constraints in the dataset ({len(self.df.loc[name, 'SMT-LIB2'])})"  # noqa: E501
                f"does not match the number of truth masks ({len(truth_masks)})"
            )

        results = []
        for i, mask in enumerate(truth_masks):
            if mask:
                results.append(self.df.loc[name, "SMT-LIB2"][i])
            else:
                results.append(self.df.loc[name, "SMT-LIB2 negation"][i])

        return results

    def get_python_programs(self, name: str, truth_masks: list[bool]) -> list[Callable]:
        functions = self.df.loc[name, "Functions"]
        results = []

        for i, mask in enumerate(truth_masks):
            func = source_code_to_function(functions[i])
            if mask:
                results.append(func)
            else:
                results.append(lambda x: not func(x))

        return results

    def get_problem(self, name: str, truth_masks: list[bool]) -> ConstraintProblem:
        return ConstraintProblem(
            nl_constraints=self.get_nl_constraints(name, truth_masks),
            smt_constraints=self.get_smt_constraints(name, truth_masks),
            python_checkers=self.get_python_programs(name, truth_masks),
            name=name,
        )


def source_code_to_function(source_code: str) -> Callable:
    """
    Extracts the function definition from the source code.

    Args:
        source_code (str): The source code of the program.

    Returns:
        Callable: The callable function object
    """
    namespace = {}
    exec(source_code, namespace)
    for name, obj in namespace.items():
        if callable(obj):
            return obj
    return None
