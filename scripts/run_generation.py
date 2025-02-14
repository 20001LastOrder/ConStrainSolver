import os
from argparse import ArgumentParser
from itertools import product

import dotenv
import pandas as pd
from tqdm import tqdm

from llm_string.constraints import ConstraintStore
from llm_string.string_solvers import get_solver
from llm_string.string_solvers.base import BaseStringSolver
from llm_string.string_validator import StringValidator

dotenv.load_dotenv()


def evaluate_constraints(
    solver: BaseStringSolver,
    name: str,
    constraint_store: ConstraintStore,
) -> list[dict]:
    num_constraint = constraint_store.get_num_constraints(name)
    truth_masks_comb = list(product([True, False], repeat=num_constraint))

    results = []
    # generate combinations of truth masks for the constraints
    for truth_masks in tqdm(truth_masks_comb, desc=f"Evaluating {name}"):
        problem = constraint_store.get_problem(name, truth_masks)
        problem = solver.solve(problem)
        results.append(
            {
                "name": name,
                "sat": problem.status,
                "result": problem.value,
                "truth_masks": truth_masks,
            }
        )

    return results


def validate_constraints(
    save_path: str, constraint_store: ConstraintStore
) -> pd.DataFrame:
    df = pd.read_csv(save_path, encoding="utf-8")
    validator = StringValidator()

    for index, row in tqdm(list(df.iterrows())):
        name = row["name"]
        result = str(row["result"])
        status = str(row.get("status", "sat" if result != "UNSAT" else "unsat"))
        result = result.replace('"', '""')

        truth_masks = list(eval(row["truth_masks"]))
        constraints = constraint_store.get_smt_constraints(name, truth_masks)

        # add assertion of result
        sat_res = validator.validate(status, constraints, result)

        if sat_res == "unknown":
            df.loc[index, "valid?"] = -1
            continue

        if status != "unsat":
            df.loc[index, "valid?"] = int(sat_res == "sat")
        else:
            df.loc[index, "valid?"] = int(sat_res == "unsat")

    return df


def main(args):
    constraint_store = ConstraintStore(file_path=args.file_path)
    names = constraint_store.get_constraint_names()
    results = []

    # Set save path
    if args.approach == "smt":
        # smt
        save_path_name = os.path.join(args.output_path, f"{args.smt_solver}")
    else:
        # llm  or validate
        if args.use_variable_name:
            save_path_name = os.path.join(args.output_path, f"{args.llm}")
        else:
            save_path_name = os.path.join(args.output_path, f"{args.llm}_no_name")

    save_path = save_path_name + ".csv"

    # if validating
    if args.approach == "validate":
        # read the csv
        df = pd.read_csv(save_path, encoding="utf-8")
        df = validate_constraints(save_path, constraint_store)
        validation_path = save_path_name + "_validation.csv"
        df.to_csv(validation_path, index=False)
        return

    solver = get_solver(args)
    for name in tqdm(names, desc="Evaluating all constraints"):
        results.extend(evaluate_constraints(solver, name, constraint_store))

    # Set save path
    if args.approach == "smt":
        save_path = os.path.join(args.output_path, f"{args.smt_solver}.csv")
    elif args.use_variable_name:
        save_path = os.path.join(args.output_path, f"{args.llm.replace(':', '-')}.csv")
    else:
        save_path = os.path.join(
            args.output_path, f"{args.llm.replace(':', '-')}_no_name.csv"
        )

    # Save CSV
    df = pd.DataFrame(results)
    print(df)
    df.to_csv(save_path, index=False)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "--approach", type=str, choices=["llm", "smt", "validate"], required=True
    )
    parser.add_argument("--file_path", type=str, required=True)
    parser.add_argument("--output_path", type=str, required=True)
    parser.add_argument("--llm_family", type=str, default="openai")
    parser.add_argument("--llm", type=str)
    parser.add_argument("--temperature", type=float, default=0.7)

    parser.add_argument("--use_variable_name", action="store_true")
    parser.add_argument("--smt_solver", type=str, choices=["z3", "z3str3", "cvc5"])

    args = parser.parse_args()
    main(args)
