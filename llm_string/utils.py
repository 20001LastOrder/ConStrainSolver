import ast
import json
import re

from langchain_core.output_parsers import PydanticOutputParser
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

code_block_string_array_pattern = re.compile(
    r"```[^\[]*((\[\s?(\"[^\"]+\",\s?)+\"[^\"]+\"\s?])|(\[\s?('[^']+',\s?)+'[^']+'\s?]))[^`]*```",
    re.DOTALL)

string_array_pattern = re.compile(
    r"(\[\s?(\"[^\"]+\",\s?)+\"[^\"]+\"\s?])|(\[\s?('[^']+',\s?)+'[^']+'\s?])",
    re.DOTALL)


class JSONPydanticOutputParser(PydanticOutputParser):
    def parse(self, output: str):
        json_pattern = re.compile(r"```(json)?\n(.*?)\n```", re.DOTALL)
        match = json_pattern.search(output)

        if match:
            json_object = json.loads(match.group(2))
            return self._parse_obj(json_object)
        else:
            raise ValueError("No JSON found in the output.")

class StringArrayOutputParser:
    def parse(self, output: str):
        # priority to match code block with string array
        code_block_match = code_block_string_array_pattern.search(output)

        if code_block_match:
            return ast.literal_eval(code_block_match.group(1))

        # fallback to match any string array expression
        matches = string_array_pattern.findall(output)

        if not matches:
            raise ValueError("No string array found in the output.", output)

        lists = [ast.literal_eval(m) for m in matches]

        # if more than one result, use heuristic method to take the longest list as the correct one
        return max(lists, key=len)

    def get_format_instructions(self):
        return """The output should be formatted as a Python list of strings.

As an example, the output should look like this:

```python
["string1", "string2", "string3"]
```
"""


def get_llm(args):
    if args.llm_family == "openai":
        return ChatOpenAI(model=args.llm, temperature=args.temperature)
    else:
        return ChatOllama(
            model=args.llm, max_new_tokens=500, temperature=args.temperature
        )
