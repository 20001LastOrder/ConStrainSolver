import os

import hydra
import pandas as pd
from hydra.utils import instantiate
from omegaconf import DictConfig
from z3 import Solver

from llm_string.constraints import ConstraintStore

def group_by_name(generator_type:str, df: pd.DataFrame) -> pd.DataFrame:
    names = df["name"].unique()

    results = [["Name", "NL description", "NL negation", "SMT-LIB2", "SMT-LIB2 negation", "Functions", "Functions negation", "SMT-LIB2 correct", "SMT-LIB2 negation correct", "Functions correct", "Functions negation correct"]]

    for name in names:
        name_df = df[df["name"] == name]

        true_mask_df = name_df[name_df["mask"] == True]
        false_mask_df = name_df[name_df["mask"] == False]

        name_constraints = []
        name_constraints_negation = []
        for i, row in enumerate(true_mask_df.iterrows()):
            constraint = f'{i + 1}. ' + row[1]["constraint"]

            name_constraints.append(constraint)

        constraints_string = "\n\n".join(name_constraints)

        for i, row in enumerate(false_mask_df.iterrows()):
            constraint = f'{i + 1}. ' + row[1]["constraint"]

            name_constraints_negation.append(constraint)

        constraints_negation_string = "\n\n".join(name_constraints_negation)

        if generator_type == 'python':
            name_results = []
            name_results_correct = []
            for i, row in enumerate(true_mask_df.iterrows()):
                if isinstance(row[1]["result"], str):
                    name_results.append(row[1]["result"].replace('this_function', f'constraint{i + 1}'))
                    try:
                        local_scope = {}
                        exec(row[1]["result"], None, local_scope)
                        name_results_correct.append("this_function" in local_scope)
                    except:
                        name_results_correct.append(False)
                else:
                    name_results.append("")
                    name_results_correct.append(False)

            results_string = str(name_results)

            name_results_negation = []
            name_results_negation_correct = []
            for i, row in enumerate(false_mask_df.iterrows()):
                if isinstance(row[1]["result"], str):
                    name_results_negation.append(row[1]["result"].replace('this_function', f'constraint{i + 1}'))
                    try:
                        local_scope = {}
                        exec(row[1]["result"], None, local_scope)
                        name_results_negation_correct.append("this_function" in local_scope)
                    except:
                        name_results_negation_correct.append(False)
                else:
                    name_results_negation.append("")
                    name_results_negation_correct.append(False)

            results_negation_string = str(name_results_negation)

            results.append([name, constraints_string, constraints_negation_string, None, None, results_string, results_negation_string, None, None, str(name_results_correct), str(name_results_negation_correct)])

        elif generator_type == 'smt':
            name_results = []
            name_results_correct = []
            for i, row in enumerate(true_mask_df.iterrows()):
                if isinstance(row[1]["result"], str):
                    name_results.append(f'{i + 1}. ' + row[1]["result"])
                    try:
                        solver = Solver()

                        solver.from_string('(declare-const s String)')
                        solver.from_string(f'(assert {row[1]["result"]})')

                        sat = solver.check()

                        name_results_correct.append(sat.r == 1)
                    except:
                        name_results_correct.append(False)
                else:
                    name_results.append("")
                    name_results_correct.append(False)

            results_string = "\n\n".join(name_results)

            name_results_negation = []
            name_results_negation_correct = []
            for i, row in enumerate(false_mask_df.iterrows()):
                if isinstance(row[1]["result"], str):
                    name_results_negation.append(f'{i + 1}. ' + row[1]["result"])
                    try:
                        solver = Solver()

                        solver.from_string('(declare-const s String)')
                        solver.from_string(f'(assert {row[1]["result"]})')

                        sat = solver.check()

                        name_results_negation_correct.append(sat.r == 1)
                    except:
                        name_results_negation_correct.append(False)
                else:
                    name_results_negation.append("")
                    name_results_negation_correct.append(False)

            results_negation_string = "\n\n".join(name_results_negation)

            results.append([name, constraints_string, constraints_negation_string, results_string, results_negation_string, None, None, str(name_results_correct), str(name_results_negation_correct), None, None])


    processed_df = pd.DataFrame(results[1:], columns=results[0])

    return processed_df


def postpostprocess(cfg: DictConfig, constraint_store: ConstraintStore):
    results = {
        "deepseek-chat-independent": [],
        "deepseek-chat-batch": [],
        "gpt-4o-independent": [],
        "gpt-4o-batch": [],
        "gpt-4o-mini-independent": [],
        "gpt-4o-mini-batch": [],
        "Meta-Llama-3.1-8B-Instruct-Turbo-128K-independent": [],
        "Meta-Llama-3.1-8B-Instruct-Turbo-128K-batch": [],
    }

    for generator_type in os.listdir(cfg.output_folder):
        generator_type_dir = os.path.join(cfg.output_folder, generator_type)
        if not os.path.isdir(generator_type_dir):
            continue

        for generator_mode in os.listdir(generator_type_dir):
            generator_mode_dir = os.path.join(cfg.output_folder, generator_type, generator_mode)

            if not os.path.isdir(generator_mode_dir):
                continue

            for run_id in os.listdir(generator_mode_dir):
                run_dir = os.path.join(cfg.output_folder, generator_type, generator_mode, run_id)

                if not os.path.isdir(run_dir):
                    continue

                for model_file in os.listdir(run_dir):
                    if not model_file.endswith(".csv"):
                        continue

                    model_name = model_file[:-4]

                    result_key = f"{model_name}-{generator_mode}"

                    df = pd.read_csv(os.path.join(run_dir, model_file), header=0)

                    processed_df = group_by_name(generator_type, df)

                    results[result_key].append(processed_df)

    for key, value in results.items():
        if len(value) == 0:
            continue

        merged_df = value[0].combine_first(value[1])

        names = constraint_store.get_constraint_names()

        merged_df["Name"] = pd.Categorical(merged_df["Name"], names, ordered=True)

        merged_df = merged_df.sort_values("Name").reset_index(drop=True)

        merged_df.index = merged_df.index.map(lambda x: f"{x + 1:02}")

        merged_df.index.rename("sample_id", inplace=True)

        merged_df.to_csv(cfg.output_folder + f"{key}.csv", index=True, header=True)

@hydra.main(version_base=None, config_path="../../../../conf", config_name="cg_validation_config_week4")
def main(cfg: DictConfig):
    constraint_store: ConstraintStore = instantiate(cfg.constraint_store)

    postpostprocess(cfg, constraint_store)

if __name__ == "__main__":
    main()