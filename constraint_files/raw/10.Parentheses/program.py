def constraint1(parentheses: str) -> bool:
    """
    A parentheses string shall only contains "(" and ")" charaters.
    """
    return all(char in "()" for char in parentheses)


def constraint2(parentheses: str) -> bool:
    """
    The total number of "(" characters shall be equal to the total number of ")" characters in a parentheses string.
    """
    return parentheses.count("(") == parentheses.count(")")


def constraint3(parentheses: str) -> bool:
    """
    When scanning from left to right on the parentheses string, at no point shall the count of ")" characters exceed the count of "(" characters.
    """
    count = 0
    for char in parentheses:
        if char == "(":
            count += 1
        elif char == ")":
            count -= 1
        if count < 0:
            return False
    return True


if __name__ == "__main__":
    parentheses = input("Enter the parentheses string: ")

    if (
        constraint1(parentheses)
        and constraint2(parentheses)
        and constraint3(parentheses)
    ):
        print("The parentheses string is valid.")
    else:
        print("The parentheses string is invalid.")
