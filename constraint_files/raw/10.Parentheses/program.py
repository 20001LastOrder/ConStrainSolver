def constraint1(parentheses: str) -> bool:
    """
    A parentheses string shall be at least 10 characters long
    """
    return len(parentheses) >= 10


def constraint2(parentheses: str) -> bool:
    """
    A parentheses string shall only contains "(" and ")" charaters.
    """
    return all(char in "()" for char in parentheses)


def constraint3(parentheses: str) -> bool:
    """
    The total number of "(" characters shall be equal to the total number of ")" characters in a parentheses string.
    """
    return parentheses.count("(") == parentheses.count(")")


def constraint4(parentheses: str) -> bool:
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
    constraints = [constraint1, constraint2, constraint3, constraint4]

    while True:
        parentheses = input("Enter the parentheses: ")
        result = True
        for i, constraint in enumerate(constraints):
            evaluation_result = constraint(parentheses)
            print(f"Constraint {i + 1}: {evaluation_result}")
            result = result and evaluation_result

        if result:
            print("The parentheses is valid.")
        else:
            print("The parentheses is invalid.")
