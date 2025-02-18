from llm_string.constraint_generator.core.constraint_evaluator import ConstraintEvaluator
from llm_string.constraint_generator.core.llm_agent import LLMAgent
from llm_string.constraint_generator.utils.logging_overrides import addConsoleToLogger, removeConsoleFromLogger, \
    getLogger


def get_constraint_evaluator(constraint: str, constraint_type: str, max_retries=0, model_name='gpt-4o-mini', temperature=0.5, verbose=False) -> ConstraintEvaluator | None:
    """
    Get a constraint evaluator from a given natural language constraint.
    :param constraint: the natural language constraint.
    :param constraint_type: the type of constraint. Accepted values are "smt-lib2" and "z3py".
    :param max_retries: the maximum number of retries for the LLM to generate the constraint.
    :param model_name: the LLM model to use. Default is "gpt-4o-mini".
    :param temperature: the temperature to use for the LLM. Default is 0.5.
    :param verbose: whether the log should also print to the console.
    :return: a constraint evaluator if the operation is successful, None otherwise.
    """
    if verbose:
        addConsoleToLogger()

    logger = getLogger("constraint_generator")

    agent = LLMAgent(constraint_type, model_name=model_name, temperature=temperature)

    try:
        evaluator = agent.get_evaluator(constraint, max_retries=max_retries)
    except Exception as e:
        logger.error("Error creating evaluator for constraint %s: %s", constraint, str(e))
        evaluator = None
    finally:
        if verbose:
            removeConsoleFromLogger()

    return evaluator

