from llm_string.constraint_generator.core.batch_constraint_generator_agent import BatchConstraintGeneratorAgent
from llm_string.constraint_generator.core.constraint_evaluator import ConstraintEvaluator
from llm_string.logging.logging_overrides import addConsoleToLogger, removeConsoleFromLogger, getLogger


def get_constraint_evaluator(
        constraint: str | list[str],
        constraint_type: str,
        generator_type='independent',
        max_retries_per_attempt=0,
        model_name='gpt-4o-mini',
        temperature=0.5,
        max_steps=10,
        use_examples=False,
        fault_tolerant=False,
        verbose=False
) -> ConstraintEvaluator | None:
    """
    Get a constraint evaluator from a given natural language constraint.
    :param constraint: the natural language constraint.
    :param constraint_type: the type of constraint. Accepted values are "smt-lib2" and "z3py".
    :param generator_type: whether the generator should evaluate constraints independently or in batch. Accepted values are "independent" and "batch".
    :param max_retries_per_attempt: the maximum number of retries for the LLM to generate the constraint.
    :param model_name: the LLM model to use. Default is "gpt-4o-mini".
    :param temperature: the temperature to use for the LLM. Default is 0.5.
    :param max_steps: the maximum number of steps for the agent to try to generate an evaluator. A step is a call to an agent, either to generate an evaluator, to generate example strings or to judge.
    :param use_examples: when True, the agent will use example generator agent to generate strings to validate the evaluator.
    :param fault_tolerant: when True and use_examples is True, the agent will return the last generated evaluator even if it fails the examples, in case no evaluator passes the examples.
    :param verbose: whether the log should also print to the console.
    :return: a constraint evaluator if the operation is successful, None otherwise.
    """
    logger_id = -1

    if verbose:
        logger_id = addConsoleToLogger()

    logger = getLogger()
    agent = BatchConstraintGeneratorAgent(constraint_type, model_name=model_name, temperature=temperature)

    try:
        evaluator = agent.get_evaluator(constraint,
                                        max_retries_per_attempt=max_retries_per_attempt,
                                        max_steps=max_steps,
        )
    except Exception as e:
        logger.error("Error creating evaluator for constraint {0}: {1}", constraint, str(e))
        evaluator = None
    finally:
        if verbose:
            removeConsoleFromLogger(logger_id)

    return evaluator

def get_constraint(
        constraint: str | list[str],
        constraint_type: str,
        generator_type='independent',
        variables: list[str]=None,
        max_retries_per_attempt=0,
        model_name='gpt-4o-mini',
        temperature=0.5,
        max_steps=10,
        use_examples=False,
        fault_tolerant=False,
        verbose=False
) -> str | None:
    """
    Get a constraint string from a given natural language constraint.
    :param constraint: the natural language constraint.
    :param constraint_type: the type of constraint. Accepted values are "smt-lib2" and "z3py".
    :param generator_type: whether the generator should evaluate constraints independently or in batch. Accepted values are "independent" and "batch".
    :param variables: the variables to use in the constraint. The default variable is a single variable named 's'.
    :param max_retries_per_attempt: the maximum number of retries for the LLM to generate the constraint.
    :param model_name: the LLM model to use. Default is "gpt-4o-mini".
    :param temperature: the temperature to use for the LLM. Default is 0.5.
    :param max_steps: the maximum number of steps for the agent to try to generate an evaluator. A step is a call to an agent, either to generate an evaluator, to generate example strings or to judge.
    :param use_examples: when True, the agent will use example generator agent to generate strings to validate the evaluator.
    :param fault_tolerant: when True and use_examples is True, the agent will return the last generated evaluator even if it fails the examples, in case no evaluator passes the examples.
    :param verbose: whether the log should also print to the console.
    :return: the string constraint in the selected constraint type if successful, None otherwise.
    """
    if variables is None:
        variables = ['s']

    evaluator = get_constraint_evaluator(
        constraint,
        constraint_type,
        generator_type,
        max_retries_per_attempt,
        model_name,
        temperature,
        max_steps,
        use_examples,
        fault_tolerant,
        verbose
    )

    if evaluator is None:
        return None

    constraint_string = evaluator.constraint.constraint

    if len(evaluator.constraint.variables) != len(variables):
        return None

    for oldVar, newVar in zip(evaluator.constraint.variables, variables):
        if isinstance(constraint_string, list):
            for i in range(len(constraint_string)):
                constraint_string[i] = constraint_string[i].replace(oldVar, newVar)
        else:
            constraint_string = constraint_string.replace(oldVar, newVar)

    return constraint_string
