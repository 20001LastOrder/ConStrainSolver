import json
import re

from langchain_core.output_parsers import PydanticOutputParser
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI


class JSONPydanticOutputParser(PydanticOutputParser):
    def parse(self, output: str):
        json_pattern = re.compile(r"```(json)?\n(.*?)\n```", re.DOTALL)
        match = json_pattern.search(output)

        if match:
            json_object = json.loads(match.group(2))
            return self._parse_obj(json_object)
        else:
            raise ValueError("No JSON found in the output.")


def get_llm(args):
    if args.llm_family == "openai":
        return ChatOpenAI(model=args.llm, temperature=args.temperature)
    else:
        return ChatOllama(
            model=args.llm, max_new_tokens=500, temperature=args.temperature
        )
