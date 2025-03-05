import os

import pandas as pd


def postprocess(run_folder_path: str):

    columns = ["name", "mask", "constraint", "result"]

    for model_name in os.listdir(run_folder_path):
        if not os.path.isdir(f"{run_folder_path}{model_name}"):
            continue

        results = []
        for name in os.listdir(f"{run_folder_path}{model_name}/"):
            for mask in [True, False]:
                process_path = f"{run_folder_path}{model_name}/{name}/{mask}/"

                with open(f"{process_path}output.csv", "r") as f:
                    constraints_df = pd.read_csv(f, header=0)

                results.extend([(name, mask, constraint, result) for constraint, result in zip(constraints_df["constraint"], constraints_df["result"])])

        df = pd.DataFrame(results, columns=columns)
        df.to_csv(f"{run_folder_path}{model_name}.csv", index=False)