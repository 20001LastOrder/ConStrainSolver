import argparse
import ast
import json
import os

import pandas as pd
from loguru import logger


def get_folders(directory):
    result = [entry.name for entry in os.scandir(directory) if entry.is_dir()]
    return sorted(result)


def extract_function_blocks(file_path: str) -> list[str]:
    with open(file_path, "r", encoding="utf-8") as file:
        source = file.read()

    # Parse the source code into an AST.
    tree = ast.parse(source)

    functions = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            # Extract the complete source segment corresponding to the function.
            code_block = ast.get_source_segment(source, node)
            functions.append(code_block)
    return functions


def process_one_sample(path: str, folder_name: str) -> dict:
    sample_id, sample_name = folder_name.split(".", 1)
    result = {
        "sample_id": sample_id,
        "Name": sample_name,
    }

    full_path = os.path.join(path, folder_name)
    # read nl content
    with open(os.path.join(full_path, "nl.txt"), "r", encoding="utf-8") as file:
        result["NL description"] = file.read()

    # read nl negation
    with open(
        os.path.join(full_path, "nl_negation.txt"), "r", encoding="utf-8"
    ) as file:
        result["NL negation"] = file.read()

    # read smt
    with open(os.path.join(full_path, "smt.txt"), "r", encoding="utf-8") as file:
        result["SMT-LIB2"] = file.read()

    # read smt negation
    with open(
        os.path.join(full_path, "smt_negation.txt"), "r", encoding="utf-8"
    ) as file:
        result["SMT-LIB2 negation"] = file.read()

    # read functions
    functions = extract_function_blocks(os.path.join(full_path, "program.py"))
    result["Functions"] = json.dumps(functions)

    return result


def main(args):
    folders = get_folders(args.input_folder)
    results = []
    for folder in folders:
        logger.info(f"Processing {folder}")
        result = process_one_sample(args.input_folder, folder)
        results.append(result)

    # Convert the results to a DataFrame and save it to a CSV file.
    df = pd.DataFrame(results)
    df.to_csv(args.output_file, index=False)
    logger.info(f"Saved the results to {args.output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract function blocks from Python files."
    )
    parser.add_argument(
        "--input_folder",
        type=str,
        help="Path to the folder containing raw dataset",
        default="constraint_files/raw",
    )
    parser.add_argument(
        "--output_file",
        type=str,
        help="Path to the output CSV file.",
        default="constraint_files/constraints.csv",
    )
    args = parser.parse_args()

    main(args)
