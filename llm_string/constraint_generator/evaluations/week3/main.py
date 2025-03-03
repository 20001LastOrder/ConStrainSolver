import json
import os
from functools import partial
from itertools import product
from multiprocessing import Pool
from random import random

import hydra
import pandas as pd
from hydra.utils import instantiate
from omegaconf import DictConfig
from tqdm import tqdm

from llm_string.constraint_generator.core.python import BatchPythonGeneratorAgent
from llm_string.constraint_generator.evaluations.week3.postprocessing import postprocess
from llm_string.constraints import ConstraintStore

def generate_functions(
        run_id: int,
        cfg: DictConfig,
        constraint_store: ConstraintStore,
        name_mask_comb: tuple[str, bool]
) -> list[tuple[str, str]]:
    name, mask = name_mask_comb

    process_path = f"{cfg.output_folder}{cfg.model_name}/{cfg.batch_size}_batch/{run_id}/{name}/{mask}"

    if not os.path.exists(process_path):
        os.makedirs(process_path)

    num_constraint = constraint_store.get_num_constraints(name)

    nl_constraints = [constraint for constraint in constraint_store.get_nl_constraints(name, [mask] * num_constraint)]

    nl_constraints_batch = [nl_constraints[i:i + cfg.batch_size] for i in range(0, len(nl_constraints), cfg.batch_size)]

    results = []

    for batch in nl_constraints_batch:
        agent = BatchPythonGeneratorAgent(
            model_name=cfg.model_name,
        )

        callable_list = agent.get_evaluator(
            constraint_text=batch,
            max_retries_per_attempt=cfg.max_retries_per_attempt,
        )

        results.extend([(nl, None) if call is None else (nl, call.source) for nl, call in zip(batch, callable_list)])

    df = pd.DataFrame(results, columns=["constraint", "function"])

    df.to_csv(f"{process_path}/output.csv", index=False)

    return results


@hydra.main(version_base=None, config_path="../../../../conf", config_name="cg_generation_config_week3")
def main(cfg: DictConfig):
    constraint_store: ConstraintStore = instantiate(cfg.constraint_store)

    name_mask_comb = list(product(constraint_store.get_constraint_names(), [True, False]))

    run_id = int(random() * 10000)

    run_path = f"{cfg.output_folder}{cfg.model_name}/{cfg.batch_size}_batch/{run_id}/"

    if not os.path.exists(run_path):
        os.makedirs(run_path)

    with open(f"{run_path}config.json", "w") as f:
        json.dump({
            "run_id": run_id,
            "model_name": cfg.model_name,
            "batch_size": cfg.batch_size,
            "max_retries_per_attempt": cfg.max_retries_per_attempt
        }, f)

    partial_generate_functions = partial(generate_functions, run_id, cfg, constraint_store)

    with Pool(processes=cfg.num_processes) as p:
        results = list(
            tqdm(
                p.imap_unordered(
                    partial_generate_functions,
                    name_mask_comb
                ),
                total=len(name_mask_comb),
                desc="Generating functions"
            )
        )

    print("Running postprocessing")
    postprocess(run_path, constraint_store)



if __name__ == "__main__":
    main()