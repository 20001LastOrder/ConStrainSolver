import json
from typing import Any, Literal

from langchain_core.output_parsers import BaseOutputParser
from langchain_core.runnables import Runnable
from loguru import logger


def generation_with_retry(
    chain: Runnable, input: Any, parser: BaseOutputParser, max_retries: int = 10
) -> Any:
    retries = 0
    while retries < max_retries:
        try:
            result = chain.invoke(input=input)
            return parser.parse(result.content).value
        except json.decoder.JSONDecodeError:
            logger.info("Error in request...")
            continue
        except ValueError:
            retries += 1
            logger.info(f"Error in output {result.content}")
            continue

    raise ValueError("Failed to generate output after multiple retries.")


def value_to_status(value: str) -> tuple[str, Literal["sat", "unsat", "unknown"]]:
    if value.strip().lower() == "unsat" or len(value) == 0:
        return ("", "unsat")
    else:
        return (value, "sat")
