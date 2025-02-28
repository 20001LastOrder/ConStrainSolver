import time

from llm_string.constraint_generator.core.constraint_generator_agent import ConstraintGeneratorAgent
from llm_string.logging.logging_overrides import addConsoleToLogger, getLogger, removeConsoleFromLogger

verbose = True
max_retries = 3

logger = getLogger()

logger.info("Starting the automation, number of retries: %d", max_retries)

default_constraint_type = "smt-lib2"

supported_types = ["smt-lib2", "z3py"]

print("Default constraint type: ", default_constraint_type)

user_input = input(f"Enter the type of constraint you want to generate, or press Enter to use the default constraint type.\nSupported types are {supported_types}: ")

constraint_type = user_input if user_input else default_constraint_type

logger.info("Constraint type received: {0}", constraint_type)

if not constraint_type in supported_types:
    logger.error(f"Invalid constraint type. Supported types are {supported_types}.")
    print(f"Invalid constraint type. Supported types are {supported_types}.")
    exit()

default_example_constraint = "If the email contains a @ character, then the email shall include a dot character (.) after the @ character but before the end."

print("Default example constraint: ", default_example_constraint)
user_input = input("Enter the natural language constraint, or press Enter to use the default example constraint: ")

constraint = user_input if user_input else default_example_constraint

logger.info("Constraint received: {0}", constraint)

logger.info("Running a new LLM agent.")

logger_id = -1

if verbose:
    logger_id = addConsoleToLogger()

agent = ConstraintGeneratorAgent(constraint_type)

evaluator = agent.get_evaluator(constraint, max_retries_per_attempt=max_retries)

if evaluator is None:
    print("Failed to create evaluator. Exiting.")
    exit(1)

time.sleep(0.2)

logger.info("LLM agent created successfully.")

if verbose:
    removeConsoleFromLogger(logger_id)

default_example_string = "JohnDoe"

number_of_variables = len(evaluator.constraint.variables)

logger.info("Detected %d variables in the constraint.", number_of_variables)
print(f"Detected {number_of_variables} variables in the constraint. Please provide a value for each variable.")

values = []

for i in range(number_of_variables):
    print(f"Variable {i + 1}: '{evaluator.constraint.variables[i]}'")
    print("Default example string: ", default_example_string)

    user_input = input("Enter a string for the value, or press Enter to use the default example string: ")

    value = user_input if user_input else default_example_string
    logger.info("Value received for variable {0}: {1}", i + 1, value)
    values.append(value)

logger.info("All values received. Values: {0}", values)
print("All values received. Values: ", values)

if verbose:
    addConsoleToLogger()

print("Sat: ", evaluator.evaluate(*values))
