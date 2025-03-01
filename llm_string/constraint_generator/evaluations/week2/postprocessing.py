import os
import json

import pandas as pd

from llm_string.constraints import ConstraintStore


def postprocess(run_folder_path: str, constraint_store: ConstraintStore):
    output_file_path = f"{run_folder_path}output.csv"

    with open(f"{run_folder_path}config.json", "r") as f:
        config = json.load(f)

    base_columns = ["name", "mask", "nl_constraint"]

    for i in range(config["max_steps"]):
        base_columns.append(f"step_{i}")


    results = []

    for name in constraint_store.get_constraint_names():
        for mask in [True, False]:
            process_path = f"{run_folder_path}/{name}/{mask}/"

            data = {}

            i = 0

            while os.path.exists(f"{process_path}{i}.json"):
                with open(f"{process_path}{i}.json", "r") as f:
                    data = json.load(f)

                nl_constraints = data["nl_constraints"]

                constraints_df = None

                with open(f"{process_path}{i}.csv", "r") as f:
                    constraints_df = pd.read_csv(f)

                constraint_dict = {}

                for l, nl_constraints in enumerate(nl_constraints):
                    constraint_dict[nl_constraints] = []
                    for j in range(config["max_steps"]):
                        row = constraints_df[constraints_df["step"] == j]

                        constraint_dict[nl_constraints].append(row[f"constraint{l}"].values[0])

                for nl_constraint, constraints in constraint_dict.items():
                    results.append([name, mask, nl_constraint] + constraints)

                i += 1

    df = pd.DataFrame(results, columns=base_columns)
    df.to_csv(output_file_path, index=False)

# postprocess("D:\\2024-2025\\Research\\core\\ConstrainSolver\\llm_string\\constraint_generator\\evaluations\\week2\\outputs\\1_batch\\5273\\", ConstraintStore("D:\\2024-2025\\Research\\core\\ConstrainSolver\\constraint_files\\independent_constraints_clamped.csv"))