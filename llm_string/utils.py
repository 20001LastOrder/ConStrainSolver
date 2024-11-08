import json
import re

from langchain_core.output_parsers import PydanticOutputParser


class JSONPydanticOutputParser(PydanticOutputParser):
    def parse(self, output: str):
        print(output)
        json_pattern = re.compile(r"```(json)?\n(.*?)\n```", re.DOTALL)
        match = json_pattern.search(output)

        if match:
            json_object = json.loads(match.group(2))
            return self._parse_obj(json_object)
        else:
            raise ValueError("No JSON found in the output.")
