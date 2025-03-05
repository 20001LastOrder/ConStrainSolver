import re
from typing import Callable


re_parse_function = re.compile(r"(def function\d+\(s: str\) -> bool:(?:(?!(`{3}|\n{3}|(def function))).)*)", re.DOTALL)
re_function_signature = re.compile(r"function\d+")


class CallableExtension(Callable):
    source: str
    call: Callable

    def __init__(self, source: str, call: Callable):
        self.source = source.strip()
        self.call = call

    def __call__(self, *args, **kwargs):
        return self.call(*args, **kwargs)


def get_template(requirements: list[str]) -> str:
    return "\n\n".join([f"def function{i + 1}(s: str) -> bool: \n    ''' Check if {requirement}'''" for i, requirement in enumerate(requirements)])


def parse(response: str) -> list[str]:
    return [match[0] for match in re_parse_function.findall(response)]


def get_functions(response: str) -> list[CallableExtension]:
    source_list = parse(response)

    local_scope = {}
    exec("\n\n".join(source_list), {}, local_scope)

    i = 1
    local_array = []

    while f"function{i}" in local_scope:
        local_array.append(local_scope[f"function{i}"])
        i += 1

    return [CallableExtension(re.sub(re_function_signature, 'this_function', source), call) for source, call in zip(source_list, local_array)]
