import re

import pandas as pd
from z3 import Solver


def transform(x: str):
    solver = Solver()

    try:
        solver.from_string("(declare-const s String)")

        if "assert" in x:
            solver.from_string(x)

            match = re.fullmatch(r"\(assert (.+)\)", x)
            return match.group(1) if match else None
        else:
            solver.from_string(f"(assert {x})")
            return x
    except Exception as e:
        print(f"Error: {e}")
        return None


def process_csv(input_file, output_file):
    # Read the CSV file
    df = pd.read_csv(input_file)

    # Ensure the 4th column (index 3) is treated as numeric
    df.iloc[:, 3] = df.iloc[:, 3].apply(transform)

    # Save the modified CSV file
    df.to_csv(output_file, index=False)


# Example usage
input_csv = "./outputs/20250224-062051/results.csv"  # Change to your actual file path
output_csv = "./outputs/20250224-062051/output.csv"
process_csv(input_csv, output_csv)