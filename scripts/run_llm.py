import os
from argparse import ArgumentParser
from itertools import product

import pandas
from langchain_core.runnables import Runnable
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from tqdm import tqdm
from z3 import Solver, sat, unsat, unknown

from constraints import ConstraintStore
from llm_string.prompt import Result, get_prompt
from llm_string.utils import JSONPydanticOutputParser

import subprocess

def call_llm(
    name: str, constraints: list[str], chain: Runnable, parser: JSONPydanticOutputParser
) -> Result:
    name = name.strip()
    constraints = "\n".join(constraints)

    while True:
        result = chain.invoke(input={"name": name, "constraints": constraints})
        try:
            return parser.parse(result.content)
        except ValueError:
            continue


def evaluate_constraints_llm(
    name: str,
    results: list[dict],
    chain: Runnable,
    constraint_store: ConstraintStore,
    parser: JSONPydanticOutputParser,
    args,
):
    num_constraint = constraint_store.get_num_constraints(name)

    # generate combinations of truth masks for the constraints
    truth_masks_comb = list(product([True, False], repeat=num_constraint))

    # get the all possible constraints
    for truth_masks in tqdm(truth_masks_comb, desc=f"Evaluating {name}"):
        constraints = constraint_store.get_nl_constraints(name, truth_masks)
        if args.use_variable_name:
            result = call_llm(name, constraints, chain, parser)
        else:
            constraints = [
                constraint.replace(name.lower(), "x") for constraint in constraints
            ]
            result = call_llm("x", constraints, chain, parser)

        results.append(
            {"name": name, "result": result.value, "truth_masks": truth_masks}
        )


def call_smt(constraints: list[str], smt_solver) -> Result:

    problem = ["(declare-const s String)"] + constraints

    if smt_solver == "cvc5":
        problem = ["(set-logic QF_SLIA)", "(set-option :strings-exp true)", "(set-option :produce-unsat-cores true)", "(set-option :produce-models true)"] + problem

        problem = problem + ["(check-sat)", "(get-model)"]
        cons_str = "\n".join(problem)

        cons_str = cons_str.replace("str.to.re", "str.to_re")
        cons_str = cons_str.replace("str.in.re", "str.in_re")
        cons_str = cons_str.replace("str.to.int", "str.to_int")
        cons_str = cons_str.replace("re.complement", "re.comp")
        
        with open("constraints.smt2", "w") as f:
            f.write(cons_str)

        result = subprocess.run(["solvers/cvc5-Win64-x86_64-static/bin/cvc5.exe", "constraints.smt2", "--tlimit=5000"], capture_output=True, text=True)
        output = result.stdout.strip()
        
        # parse outcome
        sat_res = output.split('\n')[0]

        # parse the value of s
        if sat_res == "sat":
            # Extract the value of s from the output
            string_val_line = output.split('\n')[2]
            assert string_val_line.startswith('(define-fun s () String "')

            str_val = string_val_line[len('(define-fun s () String "'):-2]


            start_index = output.find('(define-fun s () String "') + len('(define-fun s () String "')
            end_index = output.find('")', start_index)
            str_val = output[start_index:end_index]
        else:
            str_val = None

        if sat_res == "":
            sat_res = "unknown"
        return sat_res, str_val

    elif smt_solver.startswith("z3"):
        cons_str = "\n".join(problem)

        solver = Solver()
        solver.set("timeout", 30000)
        if smt_solver == "z3str3":
            solver.set("string_solver","z3str3")

        solver.from_string(cons_str)

        # call the solver
        sat_res = solver.check()
        if sat_res == sat:
            model = solver.model()
            str_val = model[model.decls()[0]]
            # str_val = str_val.as_string() # NOTE this is taking long for some reason
            # str_val = str_val.strip('"')
        else:
            str_val = None

        return sat_res, str_val


def evaluate_constraints_smt(
    name: str,
    results: list[dict],
    constraint_store: ConstraintStore,
    args,
):
    # TODO integrate other SMT solvers (maybe)
    num_constraint = constraint_store.get_num_constraints(name)
    truth_masks_comb = list(product([True, False], repeat=num_constraint))


    # generate combinations of truth masks for the constraints
    for truth_masks in tqdm(truth_masks_comb, desc=f"Evaluating {name}"):
        constraints = constraint_store.get_smt_constraints(name, truth_masks)
        sat_res, str_val = call_smt(constraints, args.smt_solver)
        results.append(
            {
                "name": name,
                "sat": sat_res,
                "result": str_val,
                "truth_masks": truth_masks,
            }
        )


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
        df = pandas.read_csv(save_path, encoding="utf-8")
        for index, row in tqdm(list(df.iterrows())):
            name = row["name"]
            result = str(row["result"])
            result = result.replace('"', '""')

            truth_masks = list(eval(row["truth_masks"]))
            constraints = constraint_store.get_smt_constraints(name, truth_masks)

            # add assertion of result
            if result != "UNSAT":
                constraints = ['(assert (= s "' + result + '"))'] + constraints

            sat_res, _ = call_smt(constraints, "z3")

            if sat_res == unknown:
                df.loc[index, "valid?"] = -1
                continue

            if result != "UNSAT":
                df.loc[index, "valid?"] = int(sat_res == sat)
            else:
                df.loc[index, "valid?"] = int(sat_res == unsat)
        validation_path = save_path_name + "_validation.csv"
        df.to_csv(validation_path, index=False)
        return

    # if not validating
    if args.approach == "llm":
        llm = (
            ChatOpenAI(model=args.llm, temperature=0.7)
            if args.llm_family == "openai"
            else ChatOllama(model=args.llm, max_new_tokens=500, temperature=0.8)
        )

        parser = JSONPydanticOutputParser(pydantic_object=Result)
        prompt = get_prompt(parser)

        chain = prompt | llm

    for name in tqdm(names, desc="Evaluating all constraints"):
        if args.approach == "llm":
            evaluate_constraints_llm(
                name, results, chain, constraint_store, parser, args
            )
        else:
            evaluate_constraints_smt(name, results, constraint_store, args)

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
    df = pandas.DataFrame(results)
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
    parser.add_argument("--use_variable_name", action="store_true")
    parser.add_argument("--smt_solver", type=str, choices=["z3", "z3str3", "cvc5"])

    args = parser.parse_args()
    main(args)
