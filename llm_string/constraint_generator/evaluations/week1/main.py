import json
import os
import time

import hydra
import pandas as pd
from hydra.utils import instantiate
from omegaconf import DictConfig
from tqdm import tqdm

from llm_string.constraint_generator.constraint_generator import get_constraint
from llm_string.constraints import ConstraintStore

BASE_SAVE_PATH = "llm_string/constraint_generator/evaluations/outputs"


def generate_one_constraint(args):
    cfg, name, constraint_comb, idx = args

    truth_mask, nl_constraint = constraint_comb

    smt_constraint = get_constraint(
        nl_constraint,
        "smt-lib2",
        model_name=cfg.model_name,
        max_retries_per_attempt=cfg.max_retries_per_attempt,
        max_steps=cfg.max_steps,
        use_examples=cfg.use_examples,
    )

    return name, truth_mask, nl_constraint, smt_constraint, idx

def generate_one_batch_constraint(args):
    cfg, name, constraint_comb, idx = args

    truth_mask, nl_constraint_batch = constraint_comb

    smt_constraint_batch = get_constraint(
        [c[1] for c in nl_constraint_batch],
        "smt-lib2",
        generator_type="batch",
        model_name=cfg.model_name,
        max_retries_per_attempt=cfg.max_retries_per_attempt,
        max_steps=cfg.max_steps,
        use_examples=cfg.use_examples,
    )

    if smt_constraint_batch is None:
        smt_constraint_batch = [None] * len(nl_constraint_batch)

    if len(smt_constraint_batch) < len(nl_constraint_batch):
        smt_constraint_batch = smt_constraint_batch + [None] * (len(nl_constraint_batch) - len(smt_constraint_batch))

    return [(name, nl_constraint[0], nl_constraint[1], smt_constraint, idx) for nl_constraint, smt_constraint in zip(nl_constraint_batch, smt_constraint_batch)]

def generate_constraints(
        cfg: DictConfig,
        name: str,
        constraint_store: ConstraintStore
):
    num_constraint = constraint_store.get_num_constraints(name)

    nl_descriptions = [(True, constraint) for constraint in constraint_store.get_nl_constraints(name, [True] * num_constraint)]
    nl_negations = [(False, constraint) for constraint in constraint_store.get_nl_constraints(name, [False] * num_constraint)]

    if cfg.independent:
        nl_constraints = nl_descriptions + nl_negations

        inputs = [
            (cfg, name, constraint, idx)
            for idx, constraint in enumerate(nl_constraints)
        ]

        results = list(
            generate_one_constraint(_input) for _input in tqdm(
                inputs,
                desc=f"Generating {name}",
            )
        )

        results = sorted(results, key=lambda x: x[4])
    else:
        print("\033[91m {}\033[00m".format(f"Generating {name}"))
        smt_descriptions = generate_one_batch_constraint((cfg, name, ((True,) * num_constraint, nl_descriptions), 0))
        smt_negations = generate_one_batch_constraint((cfg, name, ((False,) * num_constraint, nl_negations), 0))


        results = smt_descriptions + smt_negations


    return [result[:-1] for result in results]


def get_save_path():
    return BASE_SAVE_PATH + time.strftime("/%Y%m%d-%H%M%S/")


@hydra.main(version_base=None, config_path="../../../../conf", config_name="cg_generation_config")
def main(cfg: DictConfig):
    start_time = time.strftime("%Y-%m-%d %H:%M:%S")

    constraint_store: ConstraintStore = instantiate(cfg.constraint_store)

    results = []

    for name in constraint_store.get_constraint_names():
        results.extend(generate_constraints(cfg, name, constraint_store))

    df = pd.DataFrame(results)
    print(df)

    save_path = get_save_path()

    if not os.path.exists(save_path):
        os.makedirs(save_path)

    df.to_csv(save_path + "results.csv", index=False)

    # write cfg as json
    with open(save_path + "config.json", "w") as f:
        json.dump({
            "model_name": cfg.model_name,
            "max_retries_per_attempt": cfg.max_retries_per_attempt,
            "max_steps": cfg.max_steps,
            "use_examples": cfg.use_examples,
            "independent": cfg.independent,
            "start_time": start_time,
        }, f)


if __name__ == "__main__":
    main()
