def constraint1(password: str) -> bool:
    """
    The password shall be at least 4 characters long.
    """
    return len(password) >= 4


def constraint2(password: str) -> bool:
    """
    The password shall contain one of the following characters: !, #, $.
    """
    return any(char in password for char in "!#$")


def constraint3(password: str) -> bool:
    """
    The password shall contain at least one upper case characters.
    """
    return any(char.isupper() for char in password)


def constraint4(password: str) -> bool:
    """
    The password shall contain at least one lower case characters.
    """
    return any(char.islower() for char in password)


def constraint5(password: str) -> bool:
    """
    The password shall contain at least one number.
    """
    return any(char.isdigit() for char in password)


if __name__ == "__main__":
    password = input("Enter your password: ")

    if (
        constraint1(password)
        and constraint2(password)
        and constraint3(password)
        and constraint4(password)
        and constraint5(password)
    ):
        print("The password is valid.")
    else:
        print("The password is invalid.")
