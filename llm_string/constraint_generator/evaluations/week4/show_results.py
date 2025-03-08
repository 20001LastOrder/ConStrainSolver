import json
import os

import hydra
import pandas as pd
from func_timeout import FunctionTimedOut, func_timeout
from hydra.utils import instantiate
from omegaconf import DictConfig
from tabulate import tabulate
from z3 import Solver

from llm_string.constraint_generator.core.batch_constraint_generator_agent import \
    postprocess_constraint
from llm_string.constraints import ConstraintStore


def calculate_python_results(cfg: DictConfig, constraint_store: ConstraintStore):
    test_cases_root_path = "constraint_files/raw/"
    generator_modes = ["independent", "batch"]

    results = []

    for generator_mode in generator_modes:
        mode_path = f"{cfg.output_folder}python/{generator_mode}"

        for run_ids in os.listdir(mode_path):
            run_path = f"{mode_path}/{run_ids}"

            for model_name_file in os.listdir(run_path):
                if not model_name_file.endswith(".csv"):
                    continue

                model_name = model_name_file[:-4]

                df = pd.read_csv(f"{run_path}/{model_name_file}", header=0)

                total_results = len(df)

                generation_success = 0

                validation_success = 0

                for index, row in df.iterrows():
                    name = row["name"]
                    mask = row["mask"]
                    constraint = row["constraint"].replace("\r\n", "\n")
                    result = row["result"]

                    num_of_constraints = constraint_store.get_num_constraints(name)

                    name_constraints = constraint_store.get_nl_constraints(name, [mask] * num_of_constraints)

                    index_in_name_constraints = name_constraints.index(constraint)

                    ground_truth = constraint_store.get_python_programs(name, [mask])[index_in_name_constraints]

                    for numbered_name in os.listdir(test_cases_root_path):
                        if name in numbered_name:
                            test_cases_path = f"{test_cases_root_path}{numbered_name}/test_cases.json"

                            with open(test_cases_path, "r") as f:
                                test_cases = json.load(f)

                            test_inputs = test_cases[f"constraint{index_in_name_constraints + 1}"]

                            true_inputs = test_inputs["true_inputs"]

                            false_inputs = test_inputs["false_inputs"]

                            ground_truth_scope = {}

                            exec(ground_truth, {}, ground_truth_scope)

                            ground_truth_function = ground_truth_scope[list(ground_truth_scope.keys())[0]]

                            generated_scope = {}

                            try:
                                exec(result, {}, generated_scope)
                            except Exception as e:
                                continue

                            generated_function = generated_scope[list(generated_scope.keys())[0]]

                            generation_success += 1

                            for inputs in true_inputs + false_inputs:
                                try:
                                    ground_truth_output = ground_truth_function(*inputs)
                                    generated_output = generated_function(*inputs)

                                    if not mask:
                                        generated_output = not generated_output

                                    if ground_truth_output != generated_output:
                                        validation_success -= 1
                                        break
                                except Exception as e:
                                    continue

                            validation_success += 1

                results.append(('python', generator_mode, model_name, total_results, generation_success, validation_success, -1))

    return results


def calculate_smt_results(cfg: DictConfig, constraint_store: ConstraintStore):
    test_cases_root_path = "constraint_files/raw/"
    smt_csv_path = f'{cfg.output_folder}smt/smt.csv'
    smt_ignore_path = f'{cfg.output_folder}smt/smt_ignore.txt'
    generator_modes = ["independent", "batch"]

    smt_csv = pd.read_csv(smt_csv_path, header=0)

    with open(smt_ignore_path, "r") as f:
        smt_ignore = f.read().splitlines()

    for generator_mode in generator_modes:
        mode_path = f"{cfg.output_folder}smt/{generator_mode}"

        for run_ids in os.listdir(mode_path):
            run_path = f"{mode_path}/{run_ids}"

            for model_name_file in os.listdir(run_path):
                if not model_name_file.endswith(".csv"):
                    continue

                model_name = model_name_file[:-4]

                smt_csv_index = (smt_csv["model_name"] == model_name) & (smt_csv["generator_mode"] == generator_mode)

                df = pd.read_csv(f"{run_path}/{model_name_file}", header=0)

                total_results = len(df)

                generation_success = smt_csv[smt_csv_index]["generation_success"].values[0]

                formal_verification_success = smt_csv[smt_csv_index]["formal_verification_success"].values[0]

                validation_success = smt_csv[smt_csv_index]["validation_success"].values[0]

                for index, row in df.iterrows():
                    if index < smt_csv[smt_csv_index]["processed_index"].values[0]:
                        continue

                    name = row["name"]
                    mask = row["mask"]
                    constraint = row["constraint"]
                    result = postprocess_constraint(str(row["result"]))

                    num_of_constraints = constraint_store.get_num_constraints(name)

                    name_constraints = constraint_store.get_nl_constraints(name, [mask] * num_of_constraints)

                    name_ground_truth = constraint_store.get_smt_constraints(name, [mask] * num_of_constraints)

                    name_ground_truth_negation = constraint_store.get_smt_constraints(name, [not mask] * num_of_constraints)

                    index_in_name_constraints = name_constraints.index(constraint)

                    ground_truth = name_ground_truth[index_in_name_constraints]

                    ground_truth_negation = name_ground_truth_negation[index_in_name_constraints]

                    solver = Solver()

                    try:
                        solver.from_string('(declare-const s String)')
                        solver.from_string(f'(assert {result})')
                    except Exception:
                        continue

                    generation_success += 1

                    if not result in smt_ignore:
                        solver = Solver()

                        solver.from_string('(declare-const s String)')
                        solver.from_string(f'(assert {result})')
                        solver.from_string(ground_truth_negation)

                        try:
                            sat = func_timeout(1, solver.check).r
                        except FunctionTimedOut:
                            smt_csv.loc[smt_csv_index, "processed_index"] = index
                            smt_csv.loc[smt_csv_index, "generation_success"] = generation_success
                            smt_csv.loc[smt_csv_index, "formal_verification_success"] = formal_verification_success
                            smt_csv.loc[smt_csv_index, "validation_success"] = validation_success

                            smt_csv.to_csv(smt_csv_path, index=False)

                            with open(smt_ignore_path, "a") as f:
                                f.write(f"{result}\n")

                            exit(1)

                        if sat == -1:
                            solver.reset()

                            solver.from_string('(declare-const s String)')
                            solver.from_string(f'(assert (not {result}))')
                            solver.from_string(ground_truth)

                            try:
                                sat = func_timeout(1, solver.check).r
                            except FunctionTimedOut:
                                smt_csv.loc[smt_csv_index, "processed_index"] = index
                                smt_csv.loc[smt_csv_index, "generation_success"] = generation_success
                                smt_csv.loc[smt_csv_index, "formal_verification_success"] = formal_verification_success
                                smt_csv.loc[smt_csv_index, "validation_success"] = validation_success

                                smt_csv.to_csv(smt_csv_path, index=False)

                                with open(smt_ignore_path, "a") as f:
                                    f.write(f"{result}\n")

                                exit(1)

                            if sat == -1:
                                formal_verification_success += 1

                    for numbered_name in os.listdir(test_cases_root_path):
                        if name in numbered_name:
                            test_cases_path = f"{test_cases_root_path}{numbered_name}/test_cases.json"

                            with open(test_cases_path, "r") as f:
                                test_cases = json.load(f)

                            test_inputs = test_cases[f"constraint{index_in_name_constraints + 1}"]

                            true_inputs = test_inputs["true_inputs"]

                            false_inputs = test_inputs["false_inputs"]

                            solver = Solver()

                            for inputs in true_inputs + false_inputs:
                                solver.reset()
                                solver.from_string('(declare-const s String)')
                                solver.from_string(f'(assert (= s "{inputs}"))')
                                solver.from_string(ground_truth)

                                ground_truth_sat = solver.check().r

                                solver.reset()

                                solver.from_string('(declare-const s String)')
                                solver.from_string(f'(assert (= s "{inputs}"))')
                                solver.from_string(f'(assert {result})')

                                try:
                                    generation_sat = func_timeout(1, solver.check).r
                                except FunctionTimedOut:
                                    smt_csv.loc[smt_csv_index, "processed_index"] = index
                                    smt_csv.loc[smt_csv_index, "generation_success"] = generation_success
                                    smt_csv.loc[
                                        smt_csv_index, "formal_verification_success"] = formal_verification_success
                                    smt_csv.loc[smt_csv_index, "validation_success"] = validation_success

                                    smt_csv.to_csv(smt_csv_path, index=False)

                                    with open(smt_ignore_path, "a") as f:
                                        f.write(f"{result}\n")

                                    exit(1)

                                if ground_truth_sat != generation_sat:
                                    validation_success -= 1
                                    break

                            validation_success += 1

                smt_csv.loc[smt_csv_index, "processed_index"] = len(df)
                smt_csv.loc[smt_csv_index, "generation_success"] = generation_success
                smt_csv.loc[smt_csv_index, "formal_verification_success"] = formal_verification_success
                smt_csv.loc[smt_csv_index, "validation_success"] = validation_success

                smt_csv.to_csv(smt_csv_path, index=False)

    smt_csv = pd.read_csv(smt_csv_path, header=0)

    results = [('smt', generator_mode, model_name, total_results, generation_success, validation_success, formal_verification_success) for generator_mode, model_name, total_results, generation_success, formal_verification_success, validation_success in smt_csv.values]

    return results


def display_table(results: list[tuple[str, str, str, int, int, int, int]]):
    df = pd.DataFrame(results, columns=["generator_type", "generator_mode", "model_name", "total_results", "generation_success", "validation_success", "formal_verification_success"])
    df.to_csv("results.csv", index=False)

    table_columns = ["Generator Type", "Generator Mode", "Model Name", "Generation Success Rate", "Validation Success Rate", "Formal Verification Success Rate"]

    generator_type_column = df["generator_type"]

    generator_mode_column = df["generator_mode"]

    model_name_column = df["model_name"]

    generation_success_rate_column = [f"{generation_success}/{total_results} ({round(generation_success / total_results * 100, 2)}%)" for generation_success, total_results in zip(df["generation_success"], df["total_results"])]

    validation_success_rate_column = [f"{validation_success}/{total_results} ({round(validation_success / total_results * 100, 2)}%)" for validation_success, total_results in zip(df["validation_success"], df["total_results"])]

    formal_verification_success_rate_column = [("N/A" if formal_verification_success < 0 else f"{formal_verification_success}/{total_results} ({round(formal_verification_success / total_results * 100, 2)}%)") for formal_verification_success, total_results in zip(df["formal_verification_success"], df["total_results"])]

    table_data = zip(generator_type_column, generator_mode_column, model_name_column, generation_success_rate_column, validation_success_rate_column, formal_verification_success_rate_column)

    table = pd.DataFrame(table_data, columns=table_columns)

    table.style.set_properties(**{'text-align': 'center'}).set_table_styles([dict(selector='th', props=[('text-align', 'center')])])

    print(tabulate(table, headers='keys', tablefmt='pretty'))



@hydra.main(version_base=None, config_path="../../../../conf", config_name="cg_validation_config_week4")
def main(cfg: DictConfig):
    constraint_store: ConstraintStore = instantiate(cfg.constraint_store)

    python_results = calculate_python_results(cfg, constraint_store)

    smt_results = calculate_smt_results(cfg, constraint_store)

    display_table(sorted(python_results + smt_results, key=lambda x: (x[0], x[1], x[2])))

if __name__ == "__main__":
    main()