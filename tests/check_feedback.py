import dotenv
import hydra
from hydra.utils import instantiate
from loguru import logger
from omegaconf import DictConfig

from llm_string.constraints import ConstraintStore

dotenv.load_dotenv()


@hydra.main(version_base=None, config_path="../conf", config_name="generation_config")
def main(cfg: DictConfig):
    constraint_store: ConstraintStore = instantiate(cfg.constraint_store)

    solver = instantiate(cfg.string_solver)

    problem = constraint_store.get_problem("Name", [True, True, True, False, False, True])
    problem = solver.solve(problem)

    logger.info(problem.value)
    logger.info(problem.status)


if __name__ == "__main__":
    main()
