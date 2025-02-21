import hydra
import pandas as pd
from hydra.utils import instantiate
from omegaconf import DictConfig
from tqdm import tqdm

from llm_string.constraints import ConstraintStore
from llm_string.string_validator import StringValidator


def validate_constraints(
    save_path: str, constraint_store: ConstraintStore
) -> pd.DataFrame:
    df = pd.read_csv(save_path, encoding="utf-8")
    validator = StringValidator(timeout=30000)

    for index, row in tqdm(list(df.iterrows())):
        name = row["name"]
        result = str(row["result"])
        status = str(row.get("status", "sat" if result.lower() != "unsat" else "unsat"))
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


@hydra.main(version_base=None, config_path="../conf", config_name="evaluation_config")
def main(args: DictConfig):
    constraint_store = instantiate(args.constraint_store)
    # read the csv
    df = pd.read_csv(args.input_path, encoding="utf-8")
    df = validate_constraints(args.input_path, constraint_store)
    df.to_csv(args.output_path, index=False)
    return


if __name__ == "__main__":
    main()
