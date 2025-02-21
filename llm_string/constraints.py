import pandas as pd

from llm_string.string_solvers.base import ConstraintProblem


class ConstraintStore:
    file_path: str

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.df = pd.read_csv(file_path, encoding="utf-8", index_col=0)
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
        results = []
        for i, mask in enumerate(truth_masks):
            if mask:
                results.append(self.df.loc[name, "SMT-LIB2"][i])
            else:
                results.append(self.df.loc[name, "SMT-LIB2 negation"][i])

        return results

    def get_problem(self, name: str, truth_masks: list[bool]) -> ConstraintProblem:
        return ConstraintProblem(
            nl_constraints=self.get_nl_constraints(name, truth_masks),
            smt_constraints=self.get_smt_constraints(name, truth_masks),
            name=name,
        )
