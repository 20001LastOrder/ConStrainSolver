import json
import os.path

import hydra
import pandas
import pandas as pd
from func_timeout import func_timeout, FunctionTimedOut
from hydra.utils import instantiate
from omegaconf import DictConfig
from z3 import Solver, Z3Exception

from llm_string.constraints import ConstraintStore

import matplotlib.pyplot as plt

def calculate_results(run_path, constraint_store: ConstraintStore):
    # Load the constraints
    output_csv = pd.read_csv(run_path + "output.csv", header=0)

    results = []

    starting_index = 0

    try:
        results_csv = pd.read_csv(run_path + "results.csv", header=0)
        results = results_csv.values.tolist()

        starting_index = len(results)
    except FileNotFoundError:
        pass

    for row_index, output_row in enumerate(output_csv.iterrows()):
        if row_index < starting_index:
            continue

        name = output_row[1]["name"]
        mask = output_row[1]["mask"]

        num_constraints = constraint_store.get_num_constraints(name)
        nl_constraints = constraint_store.get_nl_constraints(name, [mask] * num_constraints)
        smt_constraints = constraint_store.get_smt_constraints(name, [mask] * num_constraints)
        smt_constraints_negation = constraint_store.get_smt_constraints(name, [not mask] * num_constraints)

        for i, nl_constraint in enumerate(nl_constraints):
            if nl_constraint == output_row[1]["nl_constraint"]:
                smt_constraint = smt_constraints[i]
                smt_constraint_negation = smt_constraints_negation[i]

        row_result = []

        for i in range(3, len(output_row[1])):
            generated_constraint = output_row[1][i]

            if generated_constraint is None or generated_constraint == "":
                row_result.append(0)
                continue

            solver = Solver()

            solver.from_string("(declare-const s String)")

            try:
                solver.from_string(f"(assert (not {generated_constraint}))")
            except Z3Exception as e:
                print(e)
                row_result.append(0)
                continue

            solver.from_string(smt_constraint)

            check = 0

            try:
                check = func_timeout(2, solver.check).r
            except FunctionTimedOut:
                if row_index == starting_index:
                    results.append(row_result + [-1] * ((len(output_row[1]) - 3) - len(row_result)))

                df = pandas.DataFrame(results)

                df.to_csv(run_path + "results.csv", index=False)

                exit(1)

            if check != -1:
                row_result.append(1)
                continue

            solver = Solver()

            solver.from_string("(declare-const s String)")
            solver.from_string(f"(assert {generated_constraint})")
            solver.from_string(smt_constraint_negation)

            check = 0

            try:
                check = func_timeout(2, solver.check).r
            except FunctionTimedOut:
                df = pandas.DataFrame(results)

                df.to_csv(run_path + "results.csv", index=False)

                exit(1)

            if check != -1:
                row_result.append(1)
                continue

            row_result.append(2)

        results.append(row_result)

    df = pandas.DataFrame(results)

    df.to_csv(run_path + "results.csv", index=False)

    return results


def show_tables(run_path, results: list[list[int]]):
    with open(f"{run_path}config.json", "w") as f:
        config = json.load(f)

    inverted_results = list(map(list, zip(*results)))

    total = [len(inverted_results[j]) for j in range(len(inverted_results))]
    sum_of_1s = [sum([1 for i in inverted_results[j] if i > 0]) for j in range(len(inverted_results))]
    sum_of_2s = [sum([1 for i in inverted_results[j] if i > 1]) for j in range(len(inverted_results))]

    sum_of_1s_fraction = [sum_of_1s[i] / total[i] for i in range(len(sum_of_1s))]
    sum_of_2s_fraction = [sum_of_2s[i] / total[i] for i in range(len(sum_of_2s))]

    sum_of_1s_text = [f"{sum_of_1s[i]}/{total[i]} ({round(sum_of_1s[i] / total[i] * 100, 2)}%)".center(20) for i in range(len(sum_of_1s))]
    sum_of_2s_text = [f"{sum_of_2s[i]}/{total[i]} ({round(sum_of_2s[i] / total[i] * 100, 2)}%)".center(20) for i in range(len(sum_of_2s))]
    sum_portion_text = [f"{sum_of_2s[i]}/{sum_of_1s[i]} ({round(sum_of_2s[i] / sum_of_1s[i] * 100, 2)}%)".center(20) for i in range(len(sum_of_1s))]

    steps = "Steps              | " + " | ".join([f"Step {i + 1}".center(20) for i in range(len(inverted_results))])
    syntactical_recall = "Syntactical Recall | " + " | ".join(sum_of_1s_text)
    semantical_precision = "Semantic Precision | " + " | ".join(sum_portion_text)
    overall_recall = "Overall Recall     | " + " | ".join(sum_of_2s_text)

    with open(f"{run_path}table.txt", "w") as f:
        f.write(f"Constraint Generation Results with Batch Size of {config["batch_size"]}\nmodel_name='{config["model_name"]}' use_examples={config["False"]} max_retries_per_attempt={config["max_retries_per_attempt"]}\n")
        f.write(steps + "\n")
        f.write(syntactical_recall + "\n")
        f.write(semantical_precision + "\n")
        f.write(overall_recall + "\n")

    print(steps)
    print(syntactical_recall)
    print(semantical_precision)
    print(overall_recall)

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.set_title("Constraint Generation Results with Batch Size of 4")

    ax.plot([(i + 1) for i in range(len(inverted_results))], sum_of_2s_fraction, label="Overall Recall", marker='o')
    ax.fill_between([(i + 1) for i in range(len(inverted_results))], 0, sum_of_2s_fraction, alpha=0.2)
    ax.plot([(i + 1) for i in range(len(inverted_results))], sum_of_1s_fraction, label="Syntactical Recall", marker='o')
    ax.fill_between([(i + 1) for i in range(len(inverted_results))], 0, sum_of_1s_fraction, alpha=0.2)

    ax.set_ylim(0, 1)

    ax.legend()

    plt.savefig(f"{run_path}plot.png")

    plt.show()


def show_summary_table(base_path, all_results: list[tuple[dict, list[list[int]]]]):
    processed_all_first_results_no_examples = []
    processed_all_first_results_with_examples = []
    processed_all_final_results_no_examples = []
    processed_all_final_results_with_examples = []
    processed_all_first_results_no_examples_batched = []
    processed_all_first_results_with_examples_batched = []
    processed_all_final_results_no_examples_batched = []
    processed_all_final_results_with_examples_batched = []

    for config, results in all_results:
        batch_size = config["batch_size"]

        inverted_results = list(map(list, zip(*results)))

        first_results = inverted_results[0]

        first_results_batched = sum([[0] * batch_size if 0 in first_results[i:i + batch_size] else first_results[i:i + batch_size] for i in range(0, len(first_results), batch_size)], [])

        final_results = inverted_results[-1]

        final_results_batched = sum([[0] * batch_size if 0 in final_results[i:i + batch_size] else final_results[i:i + batch_size] for i in range(0, len(final_results), batch_size)], [])

        first_syntactical_recall = sum([1 for i in first_results if i > 0])
        first_overall_recall = sum([1 for i in first_results if i > 1])

        final_syntactical_recall = sum([1 for i in final_results if i > 0])
        final_overall_recall = sum([1 for i in final_results if i > 1])

        first_syntactical_recall_batched = sum([1 for i in first_results_batched if i > 0])
        first_overall_recall_batched = sum([1 for i in first_results_batched if i > 1])

        final_syntactical_recall_batched = sum([1 for i in final_results_batched if i > 0])
        final_overall_recall_batched = sum([1 for i in final_results_batched if i > 1])

        if (config["use_examples"]):
            processed_all_first_results_with_examples.append([batch_size, first_syntactical_recall, first_overall_recall])
            processed_all_final_results_with_examples.append([batch_size, final_syntactical_recall, final_overall_recall])
            processed_all_first_results_with_examples_batched.append([batch_size, first_syntactical_recall_batched, first_overall_recall_batched])
            processed_all_final_results_with_examples_batched.append([batch_size, final_syntactical_recall_batched, final_overall_recall_batched])
        else:
            processed_all_first_results_no_examples.append([batch_size, first_syntactical_recall, first_overall_recall])
            processed_all_final_results_no_examples.append([batch_size, final_syntactical_recall, final_overall_recall])
            processed_all_first_results_no_examples_batched.append([batch_size, first_syntactical_recall_batched, first_overall_recall_batched])
            processed_all_final_results_no_examples_batched.append([batch_size, final_syntactical_recall_batched, final_overall_recall_batched])

    processed_all_results = [
        ("First Step Accuracy, no Examples, Evaluated Per Constraint", processed_all_first_results_no_examples),
        ("Final Step Accuracy, no Examples, Evaluated Per Constraint", processed_all_final_results_no_examples),
        ("First Step Accuracy, with Examples, Evaluated Per Constraint", processed_all_first_results_with_examples),
        ("Final Step Accuracy, with Examples, Evaluated Per Constraint", processed_all_final_results_with_examples),
        ("First Step Accuracy, no Examples, Evaluated Per Batch", processed_all_first_results_no_examples_batched),
        ("Final Step Accuracy, no Examples, Evaluated Per Batch", processed_all_final_results_no_examples_batched),
        ("First Step Accuracy, with Examples, Evaluated Per Batch", processed_all_first_results_with_examples_batched),
        ("Final Step Accuracy, with Examples, Evaluated Per Batch", processed_all_final_results_with_examples_batched),
    ]

    for table_data in processed_all_results:
        title_data, results_data = table_data

        table_texts = [
                          [batch_size,
                           f"{syntactical_recall}/{32} ({round(syntactical_recall / 32 * 100, 2)}%)",
                           f"{overall_recall}/{syntactical_recall} ({f"{round(overall_recall / syntactical_recall * 100, 2)}%" if syntactical_recall > 0 else 'NaN'})",
                           f"{overall_recall}/{32} ({round(overall_recall / 32 * 100, 2)}%)"]
            for batch_size, syntactical_recall, overall_recall in results_data
        ]

        table_texts = sorted(table_texts, key=lambda x: x[0])

        fig, ax = plt.subplots(figsize=(10, 6))

        ax.axis('off')

        ax.table(cellText=table_texts,
                 colLabels=["Batch Size", "Syntactical Recall", "Semantic Precision", "Overall Recall"],
                 cellLoc='center',
                 loc='center')

        ax.set_title(title_data)

        plt.savefig(f"{base_path}{title_data.replace(" ", "-").replace(",", "")}.png")

        plt.show()


@hydra.main(version_base=None, config_path="../../../../conf", config_name="cg_validation_config_week2")
def main(cfg: DictConfig):
    constraint_store: ConstraintStore = instantiate(cfg.constraint_store)

    base_output_path = "llm_string\\constraint_generator\\evaluations\\week2\\outputs\\"

    run_path = f"{base_output_path}{cfg.batch_size}_batch\\{cfg.run_id}\\"

    if os.path.exists(run_path):
        results = calculate_results(run_path, constraint_store)

        show_tables(run_path, results)
    else:
        all_results = []

        for batch_folder in os.listdir(base_output_path):
            for run_folder in os.listdir(f"{base_output_path}{batch_folder}"):
                run_path = f"{base_output_path}{batch_folder}\\{run_folder}\\"

                results = calculate_results(run_path, constraint_store)

                with open(f"{run_path}config.json", "r") as f:
                    config = json.load(f)

                all_results.append((config, results))

        show_summary_table(base_output_path, all_results)


if __name__ == "__main__":
    main()