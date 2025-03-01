from typing import Any, Literal

from langchain_core.output_parsers import BaseOutputParser
from langchain_core.runnables import Runnable
from loguru import logger


def generation_with_retry(
    chain: Runnable, input: Any, parser: BaseOutputParser, max_retries: int = 5
) -> Any:
    for _ in range(max_retries):
        result = chain.invoke(input=input)
        # logger.info(result)
        try:
            return parser.parse(result.content).value
        except ValueError:
            continue
    raise ValueError("Failed to generate output after multiple retries.")


def value_to_status(value: str) -> tuple[str, Literal["sat", "unsat", "unknown"]]:
    if value.lower() == "unsat" or len(value) == 0:
        return ("", "unsat")
    else:
        return (value, "sat")
