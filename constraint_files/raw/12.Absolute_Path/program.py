def constraint1(absolute_path: str) -> bool:
    """
    The absolute path shall start with the root directory "/".
    """
    return absolute_path.startswith("/")


def constraint2(absolute_path: str) -> bool:
    """
    The absolute path shall not contain any spaces.
    """
    return " " not in absolute_path


def constraint3(absolute_path: str) -> bool:
    """
    The absolute path shall not end with "/".
    """
    return not absolute_path.endswith("/")


def constraint4(absolute_path: str) -> bool:
    """
    The absolute path shall not contain consecutive "/" characters.
    """
    return "//" not in absolute_path


if __name__ == "__main__":
    constraints = [constraint1, constraint2, constraint3, constraint4]
    while True:
        absolute_path = input("Enter the absolute_path: ")
        result = True
        for i, constraint in enumerate(constraints):
            evaluation_result = constraint(absolute_path)
            print(f"Constraint {i + 1}: {evaluation_result}")
            result = result and evaluation_result

        if result:
            print("The absolute_path is valid.")
        else:
            print("The absolute_path is invalid.")
