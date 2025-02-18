import os


def _get_example(path: str) -> (str, str):
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), path), "r") as f:
        example_nl = f.readline().strip()
        example_c = f.read().strip()

    return example_nl, example_c


def get_z3py_example() -> (str, str):
    return _get_example("z3py/email_shall_not_contain_space_character.txt")


def get_smt_lib2_example() -> (str, str):
    return _get_example("smtlib2/email_shall_not_contain_space_character.txt")
