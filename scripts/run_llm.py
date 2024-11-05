import os
from argparse import ArgumentParser

import pandas
from langchain_core.runnables import Runnable
from langchain_openai import ChatOpenAI
from tqdm import tqdm

from constraints import ConstraintStore
from llm_string.prompt import Result, get_prompt
from llm_string.utils import JSONPydanticOutputParser


def call_llm(
    name: str, constraints: list[str], chain: Runnable, parser: JSONPydanticOutputParser
) -> Result:
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
    truth_masks = [True for _ in range(num_constraint)]

    # get the full positive constraints
    constraints = constraint_store.get_nl_constraints(name, truth_masks)
    if args.use_variable_name:
        result = call_llm(name, constraints, chain, parser)
    else:
        constraints = [
            constraint.replace(name.lower(), "x") for constraint in constraints
        ]
        result = call_llm("x", constraints, chain, parser)
    results.append(
        {"name": name, "result": result.value, "truth_masks": truth_masks.copy()}
    )

    for i in tqdm(range(num_constraint), desc=f"Evaluating {name}"):
        truth_masks[i] = False
        constraints = constraint_store.get_nl_constraints(name, truth_masks)
        result = call_llm(name, constraints, chain, parser)
        results.append(
            {"name": name, "result": result.value, "truth_masks": truth_masks.copy()}
        )
        truth_masks[i] = True


def main(args):
    llm = ChatOpenAI(model=args.llm)
    constraint_store = ConstraintStore(file_path=args.file_path)

    parser = JSONPydanticOutputParser(pydantic_object=Result)
    prompt = get_prompt(parser)

    chain = prompt | llm

    names = constraint_store.get_constraint_names()

    results = []

    for name in tqdm(names, desc="Evaluating all constraints"):
        evaluate_constraints_llm(name, results, chain, constraint_store, parser, args)

    df = pandas.DataFrame(results)
    if args.use_variable_name:
        df.to_csv(os.path.join(args.output_path, f"{args.llm}.csv"), index=False)
    else:
        df.to_csv(
            os.path.join(args.output_path, f"{args.llm}_no_name.csv"), index=False
        )


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--file_path", type=str, required=True)
    parser.add_argument("--output_path", type=str, required=True)
    parser.add_argument("--llm_family", type=str, default="openai")
    parser.add_argument("--llm", type=str, required=True)
    parser.add_argument("--use_variable_name", action="store_true")

    args = parser.parse_args()
    main(args)
