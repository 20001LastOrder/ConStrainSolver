from typing import Any

from langchain_core.output_parsers import BaseOutputParser
from langchain_core.runnables import Runnable


def generation_with_retry(
    chain: Runnable, input: Any, parser: BaseOutputParser, max_retries: int = 5
) -> Any:
    for _ in range(max_retries):
        result = chain.invoke(input=input)
        try:
            return parser.parse(result.content).value
        except ValueError:
            continue
    raise ValueError("Failed to generate output after multiple retries.")
