import json
import os
import sys
from functools import partial
from itertools import product
from multiprocessing import Pool
from random import random

import hydra
import pandas as pd
from hydra.utils import instantiate
from loguru import logger
from omegaconf import DictConfig
from tqdm import tqdm

from llm_string.constraint_generator.core.python import BatchPythonGeneratorAgent
from llm_string.constraint_generator.evaluations.postprocessing import postprocess
from llm_string.constraints import ConstraintStore

def generate_functions(
        run_id: int,
        cfg: DictConfig,
        constraint_store: ConstraintStore,
        model_name_mask_comb: tuple[str, str, bool]
) -> list[tuple[str, str]]:
    model, name, mask = model_name_mask_comb

    process_path = f"{cfg.output_folder}{cfg.generator_type}/{cfg.generator_mode}/{run_id}/{model}/{name}/{mask}"

    if not os.path.exists(process_path):
        os.makedirs(process_path)

    num_constraint = constraint_store.get_num_constraints(name)

    nl_constraints = [constraint for constraint in constraint_store.get_nl_constraints(name, [mask] * num_constraint)]

    if cfg.generator_mode == "batch":
        agent = BatchPythonGeneratorAgent(
            model_name=model,
            temperature=0.01
        )

        callable_list = agent.get_evaluator(
            constraint_text=nl_constraints,
            max_retries_per_attempt=cfg.max_retries_per_attempt,
        )

        results = [(constraint, None) if result is None else (constraint, result.source) for constraint, result in zip(nl_constraints, callable_list)]
    elif cfg.generator_mode == "independent":
        results = []

        for constraint in nl_constraints:
            agent = BatchPythonGeneratorAgent(
                model_name=model,
                temperature=0.01
            )

            callable_list = agent.get_evaluator(
                constraint_text=[constraint],
                max_retries_per_attempt=cfg.max_retries_per_attempt,
            )

            results.append((constraint, callable_list[0].source if callable_list[0] is not None else None))
    else:
        raise ValueError(f"Invalid generator mode: {cfg.generator_mode}")

    df = pd.DataFrame(results, columns=["constraint", "result"])

    df.to_csv(f"{process_path}/output.csv", index=False)

    return results


@hydra.main(version_base=None, config_path="../../../conf", config_name="cg_generation_config")
def main(cfg: DictConfig):
    logger.remove()
    logger.add(sys.stderr, level="INFO")
    logger.add("llm.log", level="DEBUG")

    constraint_store: ConstraintStore = instantiate(cfg.constraint_store)

    model_name_mask_comb = list(product(cfg.model_names, constraint_store.get_constraint_names(), [True, False]))

    run_id = int(random() * 10000)

    run_path = f"{cfg.output_folder}{cfg.generator_type}/{cfg.generator_mode}/{run_id}/"

    if not os.path.exists(run_path):
        os.makedirs(run_path)

    with open(f"{run_path}config.json", "w") as f:
        json.dump({
            "run_id": run_id,
            "generator_type": cfg.generator_type,
            "generator_mode": cfg.generator_mode,
            "model_names": list(cfg.model_names),
            "max_retries_per_attempt": cfg.max_retries_per_attempt
        }, f)

    partial_generate_functions = partial(generate_functions, run_id, cfg, constraint_store)

    with Pool(processes=cfg.num_processes) as p:
        results = list(
            tqdm(
                p.imap_unordered(
                    partial_generate_functions,
                    model_name_mask_comb
                ),
                total=len(model_name_mask_comb),
                desc="Generating functions"
            )
        )

    print("Running postprocessing")
    postprocess(run_path)



if __name__ == "__main__":
    main()