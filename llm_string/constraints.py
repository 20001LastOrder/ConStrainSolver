import json
import re

import pandas as pd
from loguru import logger

from llm_string.string_solvers.base import ConstraintProblem


def preprocessing_smt_constraints(smt_constraints: str, validaitons: list[bool]) -> str:
    smt_constraints = smt_constraints.split("\n\n")
    results = ["(assert true)" for _ in range(len(validaitons))]
    pattern = re.compile(r"(\d+)\. (.+)")
    for constraint in smt_constraints:
        match = pattern.match(constraint)
        if match is None:
            continue

        idx = int(match.group(1)) - 1
        constraint = match.group(2).strip()
        if validaitons[idx]:
            results[idx] = f"(assert {constraint})"
    return "\n\n".join(results)


def transform_generated_constraints(generated_constraint_file: str) -> pd.DataFrame:
    df = pd.read_csv(generated_constraint_file, encoding="utf-8")

    # handle SMT-LIB2
    constraints = df["SMT-LIB2"].apply(lambda x: x.replace("\r", "").strip()).tolist()
    validations = df["SMT-LIB2 correct"].apply(lambda x: eval(x)).tolist()

    constraints = [
        preprocessing_smt_constraints(c, v) for c, v in zip(constraints, validations)
    ]

    df["SMT-LIB2"] = constraints

    # # handle SMT-LIB2 negation
    constraints = (
        df["SMT-LIB2 negation"].apply(lambda x: x.replace("\r", "").strip()).tolist()
    )
    validations = df["SMT-LIB2 negation correct"].apply(lambda x: eval(x)).tolist()

    constraints = [
        preprocessing_smt_constraints(c, v) for c, v in zip(constraints, validations)
    ]
    df["SMT-LIB2 negation"] = constraints

    df["Functions"] = df["Functions"].apply(lambda x: json.dumps(eval(x)))
    df["Functions negation"] = df["Functions negation"].apply(
        lambda x: json.dumps(eval(x))
    )

    return df


class ConstraintStore:
    file_path: str

    def __init__(
        self,
        file_path: str,
        sample_ids: list[str] = None,
        generated_constraint_file: str = None,
    ):
        self.file_path = file_path
        self.df = pd.read_csv(file_path, encoding="utf-8", index_col="Name")
        self.df.fillna("", inplace=True)

        if generated_constraint_file is not None:
            logger.info(f"Loading generated constraints from {generated_constraint_file}")
            generated_df = transform_generated_constraints(generated_constraint_file)
            self.df["SMT-LIB2"] = generated_df["SMT-LIB2"].tolist()
            self.df["SMT-LIB2 negation"] = generated_df["SMT-LIB2 negation"].tolist()
            self.df["Functions"] = generated_df["Functions"].tolist()

        if sample_ids is not None:
            self.df = self.df.loc[sample_ids]

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

        self.df["Functions"] = (
            self.df["Functions"].astype(object).apply(lambda x: json.loads(x))
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
            return []
        results = []
        for i, mask in enumerate(truth_masks):
            if mask:
                results.append(self.df.loc[name, "SMT-LIB2"][i])
            else:
                results.append(self.df.loc[name, "SMT-LIB2 negation"][i])

        return results

    def get_python_programs(self, name: str, truth_masks: list[bool]) -> list[str]:
        functions = self.df.loc[name, "Functions"]
        return functions

    def get_problem(self, name: str, truth_masks: list[bool]) -> ConstraintProblem:
        return ConstraintProblem(
            nl_constraints=self.get_nl_constraints(name, truth_masks),
            smt_constraints=self.get_smt_constraints(name, truth_masks),
            truth_masks=truth_masks,
            python_programs=self.get_python_programs(name, truth_masks),
            name=name,
        )
