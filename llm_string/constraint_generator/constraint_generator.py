from llm_string.constraint_generator.core.constraint_evaluator import ConstraintEvaluator
from llm_string.constraint_generator.core.constraint_generator_agent import ConstraintGeneratorAgent
from llm_string.logging.logging_overrides import addConsoleToLogger, removeConsoleFromLogger, getLogger


def get_constraint_evaluator(constraint: str, constraint_type: str, max_retries_per_attempt=0, model_name='gpt-4o-mini', temperature=0.5, max_steps=10, use_examples=False, use_judge=False, fault_tolerant=False, verbose=False) -> ConstraintEvaluator | None:
    """
    Get a constraint evaluator from a given natural language constraint.
    :param constraint: the natural language constraint.
    :param constraint_type: the type of constraint. Accepted values are "smt-lib2" and "z3py".
    :param max_retries_per_attempt: the maximum number of retries for the LLM to generate the constraint.
    :param model_name: the LLM model to use. Default is "gpt-4o-mini".
    :param temperature: the temperature to use for the LLM. Default is 0.5.
    :param max_steps: the maximum number of steps for the agent to try to generate an evaluator. A step is a call to an agent, either to generate an evaluator, to generate example strings or to judge.
    :param use_examples: when True, the agent will use example generator agent to generate strings to validate the evaluator.
    :param use_judge: when True and use_examples is True, a judge agent will determine whether the evaluator should be accepted in case it fails the examples.
    :param fault_tolerant: when True and use_examples is True, the agent will return the last generated evaluator even if it fails the examples, in case no evaluator passes the examples.
    :param verbose: whether the log should also print to the console.
    :return: a constraint evaluator if the operation is successful, None otherwise.
    """
    if verbose:
        addConsoleToLogger()

    logger = getLogger("constraint_generator")

    agent = ConstraintGeneratorAgent(constraint_type, model_name=model_name, temperature=temperature)

    try:
        evaluator = agent.get_evaluator(constraint,
                                        max_retries_per_attempt=max_retries_per_attempt,
                                        use_examples=use_examples,
                                        use_judge=use_judge,
                                        max_steps=max_steps,
                                        fault_tolerant=fault_tolerant)
    except Exception as e:
        logger.error("Error creating evaluator for constraint %s: %s", constraint, str(e))
        evaluator = None
    finally:
        if verbose:
            removeConsoleFromLogger()

    return evaluator

def get_constraint(constraint: str, constraint_type: str, max_retries_per_attempt=0, model_name='gpt-4o-mini', temperature=0.5, max_steps=10, use_examples=False, use_judge=False, fault_tolerant=False, verbose=False) -> str | None:
    """
    Get a constraint string from a given natural language constraint.
    :param constraint: the natural language constraint.
    :param constraint_type: the type of constraint. Accepted values are "smt-lib2" and "z3py".
    :param max_retries_per_attempt: the maximum number of retries for the LLM to generate the constraint.
    :param model_name: the LLM model to use. Default is "gpt-4o-mini".
    :param temperature: the temperature to use for the LLM. Default is 0.5.
    :param max_steps: the maximum number of steps for the agent to try to generate an evaluator. A step is a call to an agent, either to generate an evaluator, to generate example strings or to judge.
    :param use_examples: when True, the agent will use example generator agent to generate strings to validate the evaluator.
    :param use_judge: when True and use_examples is True, a judge agent will determine whether the evaluator should be accepted in case it fails the examples.
    :param fault_tolerant: when True and use_examples is True, the agent will return the last generated evaluator even if it fails the examples, in case no evaluator passes the examples.
    :param verbose: whether the log should also print to the console.
    :return: the string constraint in the selected constraint type if successful, None otherwise.
    """
    evaluator = get_constraint_evaluator(constraint, constraint_type, max_retries_per_attempt, model_name, temperature, max_steps, use_examples, use_judge, fault_tolerant, verbose)

    if evaluator is None:
        return None

    return evaluator.constraint.constraint
