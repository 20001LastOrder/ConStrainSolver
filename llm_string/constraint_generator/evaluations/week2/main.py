import json
import os.path
from functools import partial
from itertools import product
from multiprocessing import Pool
from random import random

import hydra
import pandas as pd
from hydra.utils import instantiate
from omegaconf import DictConfig
from tqdm import tqdm

from llm_string.constraint_generator.core.batch_constraint_generator_agent import BatchConstraintGeneratorAgent
from llm_string.constraint_generator.core.helpers.constaint_helper import parse_constraints
from llm_string.constraint_generator.evaluations.week2.postprocessing import postprocess
from llm_string.constraints import ConstraintStore

def generate_constraints(
        run_id: int,
        cfg: DictConfig,
        constraint_store: ConstraintStore,
        name_mask_comb: tuple[str, bool]
):
    name, mask = name_mask_comb

    process_path = f"{cfg.output_folder}{cfg.batch_size}_batch/{run_id}/{name}/{mask}"

    if not os.path.exists(process_path):
        os.makedirs(process_path)

    num_constraint = constraint_store.get_num_constraints(name)

    nl_constraints = [constraint for constraint in constraint_store.get_nl_constraints(name, [mask] * num_constraint)]

    nl_constraints_batch = [nl_constraints[i:i + cfg.batch_size] for i in range(0, len(nl_constraints), cfg.batch_size)]

    for i, batch in enumerate(nl_constraints_batch):
        results = []
        with open(f"{process_path}/{i}.json", "w") as f:
            json.dump({
                "name": name,
                "mask": mask,
                "nl_constraints": batch
            }, f)


        agent = BatchConstraintGeneratorAgent(
            constraint_type="smt-lib2",
            model_name=cfg.model_name,
        )

        agent.setup_steps(
            constraint_text=batch,
            max_retries_per_attempt=cfg.max_retries_per_attempt,
            use_examples=cfg.use_examples,
        )

        current_level = 0
        current_constraints = [None] * len(batch)

        max_level = 2 if cfg.use_examples else 1

        for step in range(cfg.max_steps):
            if current_level < max_level:
                evaluator, current_level = agent.step(current_level)
                current_constraints = parse_constraints(evaluator.constraint, default=[''] * len(batch))

            results.append(current_constraints[0:len(batch)] + [current_level, step])

        df = pd.DataFrame(results, columns=[f'constraint{j}' for j in range(len(batch))] + ["level", "step"])

        df.to_csv(f"{process_path}/{i}.csv", index=False)


@hydra.main(version_base=None, config_path="../../../../conf", config_name="cg_generation_config_week2")
def main(cfg: DictConfig):
    constraint_store: ConstraintStore = instantiate(cfg.constraint_store)

    name_mask_comb = list(product(constraint_store.get_constraint_names(), [True, False]))

    run_id = int(random() * 10000)

    run_path = f"{cfg.output_folder}{cfg.batch_size}_batch/{run_id}/"

    if not os.path.exists(run_path):
        os.makedirs(run_path)

    with open(f"{run_path}config.json", "w") as f:
        json.dump({
            "run_id": run_id,
            "model_name": cfg.model_name,
            "batch_size": cfg.batch_size,
            "max_retries_per_attempt": cfg.max_retries_per_attempt,
            "max_steps": cfg.max_steps,
            "use_examples": cfg.use_examples,
        }, f)

    partial_generate_constraints = partial(generate_constraints, run_id, cfg, constraint_store)

    with Pool(processes=cfg.num_processes) as p:
        results = list(
            tqdm(
                p.imap_unordered(
                    partial_generate_constraints,
                    name_mask_comb
                ),
                total=len(name_mask_comb),
                desc="Generating constraints"
            )
        )

    print("Running postprocessing")
    postprocess(run_path, constraint_store)


if __name__ == "__main__":
    main()