import os
import json

import pandas as pd

from llm_string.constraints import ConstraintStore


def postprocess(run_folder_path: str, constraint_store: ConstraintStore):
    output_file_path = f"{run_folder_path}output.csv"

    columns = ["name", "mask", "nl_constraint", "function"]

    results = []

    for name in constraint_store.get_constraint_names():
        for mask in [True, False]:
            process_path = f"{run_folder_path}/{name}/{mask}/"

            with open(f"{process_path}output.csv", "r") as f:
                constraints_df = pd.read_csv(f, header=0)

            results.extend([(name, mask, nl_constraint, function) for nl_constraint, function in zip(constraints_df["constraint"], constraints_df["function"])])

    df = pd.DataFrame(results, columns=columns)
    df.to_csv(output_file_path, index=False)