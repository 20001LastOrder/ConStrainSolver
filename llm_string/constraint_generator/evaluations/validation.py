import hydra
import pandas as pd
import numpy as np
from hydra.utils import instantiate
from omegaconf import DictConfig
from z3 import Solver

from llm_string.constraints import ConstraintStore
from llm_string.string_validator import StringValidator


def validate_constraints(
    ground_truth_path: str,
    save_path: str,
    constraint_store: ConstraintStore
) -> pd.DataFrame:
    result_df = pd.read_csv(save_path, encoding="utf-8")
    ground_truth_df = pd.read_csv(ground_truth_path, encoding="utf-8")

    for index, row in ground_truth_df.iterrows():
        name = row["name"]
        string = str(row["result"])
        status = str(row.get("status", "sat" if string.lower() != "unsat" else "unsat"))
        string = string.replace('"', '""')

        truth_masks = list(eval(row["truth_masks"]))

        smt_constraints = []

        for nl_constraint in constraint_store.get_nl_constraints(name, truth_masks):
            smt_constraints.append(result_df[result_df["2"] == nl_constraint]["3"].values[0])

        solver = Solver()

        for smt_constraint in smt_constraints:
            if smt_constraint is not None:
                solver.add(smt_constraint)




@hydra.main(version_base=None, config_path="../../../conf", config_name="cg_validation_config")
def main(cfg: DictConfig):
    constraint_store: ConstraintStore = instantiate(cfg.constraint_store)

    validate_constraints(
        cfg.ground_truth_path,
        cfg.save_path,
        constraint_store
    )


if __name__ == "__main__":
    main()
