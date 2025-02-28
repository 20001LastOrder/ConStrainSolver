def constraint1(email: str) -> bool:
    """
    The email shall not contain a space character.
    """
    return " " not in email


def constraint2(email: str) -> bool:
    """
    The email shall not start with a @ character.
    """
    return not email.startswith("@")


def constraint3(email: str) -> bool:
    """
    The email shall have exactly one @ character.
    """
    return email.count("@") == 1


def constraint4(email: str) -> bool:
    """
    If the email contains a @ character, then the email shall include a dot character (.) after the @ character but before the end.
    """
    if "@" in email:
        return "." in email.split("@")[1]
    return True


def constraint5(email: str) -> bool:
    """
    The final character of the email shall not be a dot character (.).
    """
    return not email.endswith(".")


def constraint6(email: str) -> bool:
    """
    The email shall not contain the word “manager
    """
    return "manager" not in email


if __name__ == "__main__":
    email = input("Enter your email: ")

    if (
        constraint1(email)
        and constraint2(email)
        and constraint3(email)
        and constraint4(email)
        and constraint5(email)
        and constraint6(email)
    ):
        print("The email is valid.")
    else:
        print("The email is invalid.")
