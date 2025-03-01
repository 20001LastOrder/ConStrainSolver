def constraint1(absolute_path: str) -> bool:
    """
    The absolute path shall have at least 10 characters
    """
    return len(absolute_path) >= 10


def constraint2(absolute_path: str) -> bool:
    """
    The absolute path shall start with the root directory "/".
    """
    return absolute_path.startswith("/")


def constraint3(absolute_path: str) -> bool:
    """
    The absolute path shall not contain any spaces.
    """
    return " " not in absolute_path


def constraint4(absolute_path: str) -> bool:
    """
    The absolute path shall not end with "/".
    """
    return not absolute_path.endswith("/")


def constraint5(absolute_path: str) -> bool:
    """
    The absolute path shall not contain consecutive "/" characters.
    """
    return "//" not in absolute_path


if __name__ == "__main__":
    absolute_path = input("Enter the absolute path: ")

    if (
        constraint1(absolute_path)
        and constraint2(absolute_path)
        and constraint3(absolute_path)
        and constraint4(absolute_path)
        and constraint5(absolute_path)
    ):
        print("The absolute path is valid.")
    else:
        print("The absolute path is invalid.")
