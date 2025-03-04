import os

import hydra
import pandas as pd
from hydra.utils import instantiate
from matplotlib import pyplot as plt
from omegaconf import DictConfig

from llm_string.constraints import ConstraintStore

def calculate_results(cfg: DictConfig):
    model_names = os.listdir(cfg.output_folder)

    results = {"model_name": []}

    for model_name in model_names:
        results["model_name"].append(model_name)

        batch_sizes = os.listdir(f"{cfg.output_folder}{model_name}")

        for batch_size in batch_sizes:
            if batch_size not in results:
                results[batch_size] = []

            model_result = [0, 0]

            run_ids = os.listdir(f"{cfg.output_folder}{model_name}/{batch_size}")

            for run_id in run_ids:
                df = pd.read_csv(f"{cfg.output_folder}{model_name}/{batch_size}/{run_id}/output.csv", header=0)

                model_result[0] += len(df)
                model_result[1] += len(df[df.function.notnull()])

            results[batch_size].append(model_result)

    return results


def display_table(results: dict):
    model_names = results["model_name"]

    del(results["model_name"])

    result_array = []

    columns = sorted(results.keys())

    for column in columns:
        result_array.append([f"{result[1]}/{result[0]} ({round(result[1] / result[0] * 100, 2)}%)" for result in results[column]])

    result_array = list(map(list, zip(*result_array)))

    plt.table(cellText=result_array, colLabels=columns, rowLabels=model_names, loc="center", colWidths=[0.2] * len(columns))

    plt.axis("off")
    plt.title("Recall of different LLM\nat generating syntactically correct Python functions based on constraints")
    plt.show()




@hydra.main(version_base=None, config_path="../../../../conf", config_name="cg_validation_config_week3")
def main(cfg: DictConfig):
    constraint_store: ConstraintStore = instantiate(cfg.constraint_store)

    results = calculate_results(cfg)

    display_table(results)



if __name__ == "__main__":
    main()