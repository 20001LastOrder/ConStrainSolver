import time

from llm_string.constraint_generator.core.constraint_generator_agent import ConstraintGeneratorAgent
from llm_string.logging.logging_overrides import getLogger, addConsoleToLogger

verbose = True
max_retries = 0

logger = getLogger("main")

if verbose:
    addConsoleToLogger()

constraints = [
    "The email shall contain a space character.",
    "The email shall start with a @ character.",
    "The email shall have either no @ characters or more than one @ character.",
    "If the email contains a @ character, then the email shall not include any dot characters (.) after the @ character and before the end.",
    "The final character of the email shall be a dot character (.).",
    "The email shall contain the word 'manager'.",
    "The password shall contain less than 4 characters.",
    "The password shall not contain any of the following characters: !, #, $.",
    "The password shall not contain any upper case characters.",
    "The password shall not contain any lower case characters.",
    "The password shall not contain any numbers.",
    "The date shall contain either no hyphens, one hyphen, or more than two hyphens.",
    "If there is at least one hyphen, the part before the first hyphen shall be either a number smaller than 0 or a number larger than 2025.",
    "If there are at least two hyphens, the part after the first hyphen but before the second hyphen shall be a number smaller than 1 or a number larger than 12.",
    "If there are at least two hyphens, the part after the second hyphen shall be a number smaller than 1 or larger than 31."
]

supported_types = ["smt-lib2", "z3py"]

failed = 0

for _type in supported_types:
    for constraint in constraints:
        logger.info(f"Constraint received: %s", constraint)

        logger.info("Running a new LLM agent.")

        agent = ConstraintGeneratorAgent(_type)

        evaluator = agent.get_evaluator(constraint, max_retries_per_attempt=max_retries)

        if evaluator is None:
            print("Failed to create evaluator.")
            failed += 1
            continue

        time.sleep(0.2)

        logger.info("LLM agent created successfully.")

        values = []

        for variable in evaluator.constraint.variables:
            values.append("JohnDoe")

        logger.info("All values received. Values: ", values)

        print("Sat: ", evaluator.evaluate(*values))


logger.info("Performed %d tests. %d failed.", len(supported_types) * len(constraints), failed)