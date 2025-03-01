def constraint1(name: str) -> bool:
    """
    The name shall only contain letters a-z, letters A-Z and space characters.
    """
    return all(c.isalpha() or c.isspace() for c in name)


def constraint2(name: str) -> bool:
    """
    The name shall contain at least one space character.
    """
    return any(c.isspace() for c in name)


def constraint3(name: str) -> bool:
    """
    The name shall not end with a space character.
    """
    return not name.endswith(" ")


def constraint4(name: str) -> bool:
    """
    The name shall not start with a space character.
    """
    return not name.startswith(" ")


def constraint5(name: str) -> bool:
    """
    The first character in the name shall be capitalized.
    """
    return name[0].isupper()


def constraint6(name: str) -> bool:
    """
    Any character in the name following a space character shall be capitalized.
    """
    for i in range(0, len(name) - 1):
        if name[i].isspace():
            if not name[i + 1].isupper():
                return False
    return True


if __name__ == "__main__":
    name = input("Enter your name: ")
    if (
        constraint1(name)
        and constraint2(name)
        and constraint3(name)
        and constraint4(name)
        and constraint5(name)
        and constraint6(name)
    ):
        print("The name is valid.")
    else:
        print("The name is invalid.")
