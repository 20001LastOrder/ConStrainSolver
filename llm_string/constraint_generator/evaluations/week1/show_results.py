import json
import os

import hydra
import pandas as pd
import matplotlib.pyplot as plt
from func_timeout import FunctionTimedOut, func_timeout

from hydra.utils import instantiate
from omegaconf import DictConfig
from z3 import Solver

from llm_string.constraints import ConstraintStore

result_store_csv = "llm_string/constraint_generator/evaluations/outputs/result_store.csv"


def compute_accurate_results(folder_name: str, constraint_store: ConstraintStore, result: pd.DataFrame):
    nozero_results = result[result["3"].notna()]

    result_store = pd.read_csv(result_store_csv, header=0)

    solver = Solver()

    for res in nozero_results.iterrows():
        name = res[1]["0"]
        truth_mask = res[1]["1"]
        nl_constraint = res[1]["2"]
        smt_constraint = res[1]["3"]

        processed_row = result_store[(result_store["Folder name"] == folder_name) & (result_store["Constraint"] == nl_constraint) & (result_store["Processed"] == True)]

        if not processed_row.empty:
            continue

        store_row = constraint_store.df.loc[name]

        nl_constraint_list = store_row["NL description"] if truth_mask else store_row["NL negation"]

        index = nl_constraint_list.index(nl_constraint)

        smt_ground_truth = store_row["SMT-LIB2"][index] if truth_mask else store_row["SMT-LIB2 negation"][index]
        smt_ground_truth_negation = store_row["SMT-LIB2 negation"][index] if truth_mask else store_row["SMT-LIB2"][index]

        solver.reset()

        solver.from_string("(declare-const s String)")
        solver.from_string(smt_ground_truth)
        solver.from_string(f"(assert (not {smt_constraint}))")

        try:
            sat_negation = func_timeout(2, solver.check).r
        except FunctionTimedOut:
            sat_negation = 0

        if sat_negation != -1:
            with open(result_store_csv, "a", encoding="utf-8") as f:
                f.write(f"{folder_name},\"{nl_constraint}\",{False},{True}\n")
            continue

        solver.reset()
        solver.from_string("(declare-const s String)")
        solver.from_string(smt_ground_truth_negation)
        solver.from_string(f"(assert {smt_constraint})")

        try:
            negation_sat = func_timeout(2, solver.check).r
        except FunctionTimedOut:
            negation_sat = 0

        with open(result_store_csv, "a", encoding="utf-8") as f:
            f.write(f"{folder_name},\"{nl_constraint}\",{negation_sat == -1},{True}\n")

    final_csv = pd.read_csv(result_store_csv, header=0)

    return final_csv[(final_csv["Folder name"] == folder_name) & (final_csv["Processed"] == True) & (final_csv["Correct"] == True)].shape[0]


def compute_result_dict(constraint_store: ConstraintStore):
    directory = "llm_string/constraint_generator/evaluations/outputs"
    dict_list = {}

    # Iterate through subdirectories
    for subdir in os.listdir(directory):
        subdir_path = os.path.join(directory, subdir)
        results_file = os.path.join(subdir_path, "results.csv")
        config_file = os.path.join(subdir_path, "config.json")

        if os.path.isdir(subdir_path) and os.path.isfile(results_file):
            # Read the CSV file
            df = pd.read_csv(results_file, header=0)

            with open(config_file, "r") as f:
                config = json.load(f)
                key_name = config["model_name"] + "-use-examples-" + str(config["use_examples"]) + "-independent-" + str(config["independent"])

                print(f"Computing accuracy results of {subdir_path}")

                accurate_results = compute_accurate_results(subdir_path, constraint_store, df)

                if key_name not in dict_list:
                    dict_list[key_name] = [
                        config["model_name"],
                        config["use_examples"],
                        config["independent"],
                        accurate_results,
                        int(df["3"].notna().sum()),
                        len(df)
                    ]
                else:
                    dict_list[key_name][3] += accurate_results
                    dict_list[key_name][4] += int(df["3"].notna().sum())
                    dict_list[key_name][5] += len(df)

    return dict_list


def show_tables(results: dict):
    processed_data = []
    for key, value in results.items():
        acc, syn, _all = value[3], value[4], value[5]
        precision = (acc / syn) * 100
        recall = (syn / _all) * 100
        total_recall = (acc / _all) * 100
        processed_data.append(
            [value[0], value[1], value[2], f"{syn}/{_all} ({recall:.2f}%)", f"{acc}/{syn} ({precision:.2f}%)",
             f"{acc}/{_all} ({total_recall:.2f}%)", total_recall])

    processed_data = sorted(processed_data, key=lambda x: x[6], reverse=True)

    processed_data = [data[:6] for data in processed_data]

    # Create table plot
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_axis_off()

    table_data = [["Model Name", "Using Examples?", "Independent Generation?", "Syntactical Recall",
                   "Semantic Precision", "Overall Recall"]] + processed_data

    table = ax.table(cellText=table_data, colLabels=None, cellLoc='center', loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.auto_set_column_width([0, 1, 2, 3])

    plt.title("Precision and Recall of Constraint Generation Models")
    plt.show()

    total_gpt4o = [sum([value[3] for key, value in results.items() if value[0] == "gpt-4o"]),
                   sum([value[4] for key, value in results.items() if value[0] == "gpt-4o"]),
                   sum([value[5] for key, value in results.items() if value[0] == "gpt-4o"])]
    total_gpt4o_mini = [sum([value[3] for key, value in results.items() if value[0] == "gpt-4o-mini"]),
                        sum([value[4] for key, value in results.items() if value[0] == "gpt-4o-mini"]),
                        sum([value[5] for key, value in results.items() if value[0] == "gpt-4o-mini"])]
    total_use_examples = [sum([value[3] for key, value in results.items() if value[1] == True]),
                          sum([value[4] for key, value in results.items() if value[1] == True]),
                          sum([value[5] for key, value in results.items() if value[1] == True])]
    total_not_use_examples = [sum([value[3] for key, value in results.items() if value[1] == False]),
                              sum([value[4] for key, value in results.items() if value[1] == False]),
                              sum([value[5] for key, value in results.items() if value[1] == False])]
    total_independent = [sum([value[3] for key, value in results.items() if value[2] == True]),
                         sum([value[4] for key, value in results.items() if value[2] == True]),
                         sum([value[5] for key, value in results.items() if value[2] == True])]
    total_not_independent = [sum([value[3] for key, value in results.items() if value[2] == False]),
                             sum([value[4] for key, value in results.items() if value[2] == False]),
                             sum([value[5] for key, value in results.items() if value[2] == False])]

    processed_data_2 = []

    processed_data_2.append(
        ["model_name='gpt-4o'", f"{total_gpt4o[1]}/{total_gpt4o[2]} ({(total_gpt4o[1] / total_gpt4o[2]) * 100:.2f}%)",
         f"{total_gpt4o[0]}/{total_gpt4o[1]} ({(total_gpt4o[0] / total_gpt4o[1]) * 100:.2f}%)",
         f"{total_gpt4o[0]}/{total_gpt4o[2]} ({(total_gpt4o[0] / total_gpt4o[2]) * 100:.2f}%)",
         (total_gpt4o[0] / total_gpt4o[2]) * 100])
    processed_data_2.append(["model_name='gpt-4o-mini'",
                             f"{total_gpt4o_mini[1]}/{total_gpt4o_mini[2]} ({(total_gpt4o_mini[1] / total_gpt4o_mini[2]) * 100:.2f}%)",
                             f"{total_gpt4o_mini[0]}/{total_gpt4o_mini[1]} ({(total_gpt4o_mini[0] / total_gpt4o_mini[1]) * 100:.2f}%)",
                             f"{total_gpt4o_mini[0]}/{total_gpt4o_mini[2]} ({(total_gpt4o_mini[0] / total_gpt4o_mini[2]) * 100:.2f}%)",
                             (total_gpt4o_mini[0] / total_gpt4o_mini[2]) * 100])
    processed_data_2.append(["use_examples=True",
                             f"{total_use_examples[1]}/{total_use_examples[2]} ({(total_use_examples[1] / total_use_examples[2]) * 100:.2f}%)",
                             f"{total_use_examples[0]}/{total_use_examples[1]} ({(total_use_examples[0] / total_use_examples[1]) * 100:.2f}%)",
                             f"{total_use_examples[0]}/{total_use_examples[2]} ({(total_use_examples[0] / total_use_examples[2]) * 100:.2f}%)",
                             (total_use_examples[0] / total_use_examples[2]) * 100])
    processed_data_2.append(["use_examples=False",
                             f"{total_not_use_examples[1]}/{total_not_use_examples[2]} ({(total_not_use_examples[1] / total_not_use_examples[2]) * 100:.2f}%)",
                             f"{total_not_use_examples[0]}/{total_not_use_examples[1]} ({(total_not_use_examples[0] / total_not_use_examples[1]) * 100:.2f}%)",
                             f"{total_not_use_examples[0]}/{total_not_use_examples[2]} ({(total_not_use_examples[0] / total_not_use_examples[2]) * 100:.2f}%)",
                             (total_not_use_examples[0] / total_not_use_examples[2]) * 100])
    processed_data_2.append(["independent=True",
                             f"{total_independent[1]}/{total_independent[2]} ({(total_independent[1] / total_independent[2]) * 100:.2f}%)",
                             f"{total_independent[0]}/{total_independent[1]} ({(total_independent[0] / total_independent[1]) * 100:.2f}%)",
                             f"{total_independent[0]}/{total_independent[2]} ({(total_independent[0] / total_independent[2]) * 100:.2f}%)",
                             (total_independent[0] / total_independent[2]) * 100])
    processed_data_2.append(["independent=False",
                             f"{total_not_independent[1]}/{total_not_independent[2]} ({(total_not_independent[1] / total_not_independent[2]) * 100:.2f}%)",
                             f"{total_not_independent[0]}/{total_not_independent[1]} ({(total_not_independent[0] / total_not_independent[1]) * 100:.2f}%)",
                             f"{total_not_independent[0]}/{total_not_independent[2]} ({(total_not_independent[0] / total_not_independent[2]) * 100:.2f}%)",
                             (total_not_independent[0] / total_not_independent[2]) * 100])

    processed_data_2 = [data[:4] for data in processed_data_2]

    # Create table plot
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_axis_off()

    table_data_2 = [["Configuration", "Syntactical Recall", "Semantic Precision", "Overall Recall"]] + processed_data_2

    table = ax.table(cellText=table_data_2, colLabels=None, cellLoc='center', loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.auto_set_column_width([0, 1, 2, 3])

    plt.title("Precision and Recall of Constraint Generation Models")

    plt.show()


def show_compact_tables(results: dict):
    processed_data = []
    for key, value in results.items():
        acc, syn, _all = value[3], value[4], value[5]
        precision = (acc / syn) * 100
        recall = (syn / _all) * 100
        total_recall = (acc / _all) * 100
        processed_data.append(
            [value[0], value[1], value[2], f"{recall:.2f}%", f"{precision:.2f}%",
             f"{total_recall:.2f}%", total_recall])

    processed_data = sorted(processed_data, key=lambda x: x[6], reverse=True)

    processed_data = [data[:6] for data in processed_data]

    # Create table plot
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_axis_off()

    table_data = [["Model Name", "Using Examples?", "Independent Generation?", "Syntactical Recall",
                   "Semantic Precision", "Overall Recall"]] + processed_data

    table = ax.table(cellText=table_data, colLabels=None, cellLoc='center', loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.auto_set_column_width([0, 1, 2, 3])

    plt.title("Precision and Recall of Constraint Generation Models")
    plt.show()

    total_gpt4o = [sum([value[3] for key, value in results.items() if value[0] == "gpt-4o"]),
                   sum([value[4] for key, value in results.items() if value[0] == "gpt-4o"]),
                   sum([value[5] for key, value in results.items() if value[0] == "gpt-4o"])]
    total_gpt4o_mini = [sum([value[3] for key, value in results.items() if value[0] == "gpt-4o-mini"]),
                        sum([value[4] for key, value in results.items() if value[0] == "gpt-4o-mini"]),
                        sum([value[5] for key, value in results.items() if value[0] == "gpt-4o-mini"])]
    total_use_examples = [sum([value[3] for key, value in results.items() if value[1] == True]),
                          sum([value[4] for key, value in results.items() if value[1] == True]),
                          sum([value[5] for key, value in results.items() if value[1] == True])]
    total_not_use_examples = [sum([value[3] for key, value in results.items() if value[1] == False]),
                              sum([value[4] for key, value in results.items() if value[1] == False]),
                              sum([value[5] for key, value in results.items() if value[1] == False])]
    total_independent = [sum([value[3] for key, value in results.items() if value[2] == True]),
                         sum([value[4] for key, value in results.items() if value[2] == True]),
                         sum([value[5] for key, value in results.items() if value[2] == True])]
    total_not_independent = [sum([value[3] for key, value in results.items() if value[2] == False]),
                             sum([value[4] for key, value in results.items() if value[2] == False]),
                             sum([value[5] for key, value in results.items() if value[2] == False])]

    processed_data_2 = []

    processed_data_2.append(
        ["model_name='gpt-4o'", f"{(total_gpt4o[1] / total_gpt4o[2]) * 100:.2f}%",
         f"{(total_gpt4o[0] / total_gpt4o[1]) * 100:.2f}%",
         f"{(total_gpt4o[0] / total_gpt4o[2]) * 100:.2f}%",
         (total_gpt4o[0] / total_gpt4o[2]) * 100])
    processed_data_2.append(["model_name='gpt-4o-mini'",
                             f"{(total_gpt4o_mini[1] / total_gpt4o_mini[2]) * 100:.2f}%",
                             f"{(total_gpt4o_mini[0] / total_gpt4o_mini[1]) * 100:.2f}%",
                             f"{(total_gpt4o_mini[0] / total_gpt4o_mini[2]) * 100:.2f}%",
                             (total_gpt4o_mini[0] / total_gpt4o_mini[2]) * 100])
    processed_data_2.append(["use_examples=True",
                             f"{(total_use_examples[1] / total_use_examples[2]) * 100:.2f}%",
                             f"{(total_use_examples[0] / total_use_examples[1]) * 100:.2f}%",
                             f"{(total_use_examples[0] / total_use_examples[2]) * 100:.2f}%",
                             (total_use_examples[0] / total_use_examples[2]) * 100])
    processed_data_2.append(["use_examples=False",
                             f"{(total_not_use_examples[1] / total_not_use_examples[2]) * 100:.2f}%",
                             f"{(total_not_use_examples[0] / total_not_use_examples[1]) * 100:.2f}%",
                             f"{(total_not_use_examples[0] / total_not_use_examples[2]) * 100:.2f}%",
                             (total_not_use_examples[0] / total_not_use_examples[2]) * 100])
    processed_data_2.append(["independent=True",
                             f"{(total_independent[1] / total_independent[2]) * 100:.2f}%",
                             f"{(total_independent[0] / total_independent[1]) * 100:.2f}%",
                             f"{(total_independent[0] / total_independent[2]) * 100:.2f}%",
                             (total_independent[0] / total_independent[2]) * 100])
    processed_data_2.append(["independent=False",
                             f"{(total_not_independent[1] / total_not_independent[2]) * 100:.2f}%",
                             f"{(total_not_independent[0] / total_not_independent[1]) * 100:.2f}%",
                             f"{(total_not_independent[0] / total_not_independent[2]) * 100:.2f}%",
                             (total_not_independent[0] / total_not_independent[2]) * 100])

    processed_data_2 = [data[:4] for data in processed_data_2]

    # Create table plot
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_axis_off()

    table_data_2 = [["Configuration", "Syntactical Recall", "Semantic Precision", "Overall Recall"]] + processed_data_2

    table = ax.table(cellText=table_data_2, colLabels=None, cellLoc='center', loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.auto_set_column_width([0, 1, 2, 3])

    plt.title("Precision and Recall of Constraint Generation Models")

    plt.show()

@hydra.main(version_base=None, config_path="../../../../conf", config_name="cg_validation_config")
def main(cfg: DictConfig):
    constraint_store: ConstraintStore = instantiate(cfg.constraint_store)

    results = compute_result_dict(constraint_store)
    # with open("llm_string/constraint_generator/evaluations/outputs/results.json", "r") as f:
    #     results = json.load(f)

    show_compact_tables(results)

    with open("llm_string/constraint_generator/evaluations/outputs/results.json", "w") as f:
        json.dump(results, f)


if __name__ == "__main__":
    main()