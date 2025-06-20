import os
from itertools import product
from multiprocessing import Pool

import dotenv
import hydra
import pandas as pd
from hydra.utils import instantiate
from loguru import logger
from omegaconf import DictConfig
from tqdm import tqdm

from llm_string.constraints import ConstraintStore
from llm_string.string_solvers.base import ConstraintProblem

dotenv.load_dotenv()


def solve_one_problem(args) -> ConstraintProblem:
    config, problem, idx = args
    logger.remove()
    logger.add(
        os.path.join(config.output_folder, "log.txt"),
        level="INFO",
        colorize=False,
        backtrace=True,
        diagnose=True,
    )

    solver = instantiate(config.string_solver)
    problem = solver.solve(problem)

    result = {
        "status": problem.status,
        "result": problem.value,
    }

    return result, idx


def evaluate_constraints(
    config: DictConfig,
    name: str,
    constraint_store: ConstraintStore,
) -> list[dict]:
    num_constraint = constraint_store.get_num_constraints(name)
    truth_masks_comb = list(product([True, False], repeat=num_constraint))

    results = []

    inputs = [
        (config, constraint_store.get_problem(name, truth_masks), idx)
        for idx, truth_masks in enumerate(truth_masks_comb)
    ]
    # generate combinations of truth masks for the constraints
    with Pool(processes=config.num_processes) as p:
        results = list(
            tqdm(
                p.imap_unordered(solve_one_problem, inputs),
                total=len(inputs),
                desc=f"Evaluating {name} with {config.num_processes} processes",
            )
        )

    results = sorted(results, key=lambda x: x[1])

    result_dicts = []
    for result, idx in results:
        result["name"] = name
        result["truth_masks"] = truth_masks_comb[idx]
        result_dicts.append(result)

    return result_dicts


@hydra.main(version_base=None, config_path="../conf", config_name="generation_config")
def main(cfg: DictConfig):
    string_solver = cfg.string_solver
    constraint_store: ConstraintStore = instantiate(cfg.constraint_store)

    names = constraint_store.get_constraint_names()
    results = []

    if hasattr(string_solver, "llm"):
        name = string_solver.llm.model
        if "/" in name:
            name = name.split("/")[-1]
        save_path = f"{cfg.output_folder}/{name}.csv"
    else:
        save_path = f"{cfg.output_folder}/{string_solver.solver_name}.csv"

    for name in tqdm(names, desc="Evaluating all constraints"):
        results.extend(evaluate_constraints(cfg, name, constraint_store))
        # Save CSV for each case
        df = pd.DataFrame(results)
        df.to_csv(save_path, index=False)


if __name__ == "__main__":
    main()
