from llm_string.logging.logging_overrides import getLogger, addConsoleToLogger, removeConsoleFromLogger
from llm_string.string_generator.core.string_generator_agent import StringGeneratorAgent

verbose = True

logger = getLogger()

logger_id = -1

if verbose:
    logger_id = addConsoleToLogger()

agent = StringGeneratorAgent()

constraint = "If the email contains a @ character, then the email shall include a dot character (.) after the @ character but before the end."

logger.info("Calling the agent.")

items = agent.generate_strings(constraint, 2, 3)

logger.info("Agent run successfully.")

if verbose:
    removeConsoleFromLogger(logger_id)

print("Items generated: ", items)

