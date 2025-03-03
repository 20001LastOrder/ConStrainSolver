def constraint1(expression: str) -> bool:
    """
    An arithmetic expression shall only contain digits (0-9) and arithmetic operators (+, -, *, /).
    """
    return all(char.isdigit() or char in "+-*/" for char in expression)


def constraint2(expression: str) -> bool:
    """
    The arithmetic operators (+, -, *, /) in an arithmetic expression shall not appear consecutively.
    """
    patterns = [
        "++",
        "--",
        "**",
        "//",
        "+-",
        "-+",
        "*/",
        "/*",
        "/-",
        "-/",
        "+/",
        "/+",
        "*-",
        "-*",
        "*+",
        "+*",
    ]
    return not any(pattern in expression for pattern in patterns)


def constraint3(expression: str) -> bool:
    """
    Except for the minus sign (-), every operator (+, *, /) shall have a number before and after it.
    """
    for i in range(len(expression)):
        if expression[i] in "+*/" and (
            i == 0
            or not expression[i - 1].isdigit()
            or i == len(expression) - 1
            or not expression[i + 1].isdigit()
        ):
            return False
    return True


def constraint4(expression: str) -> bool:
    """
    An expression shall not start with operators +, *, /.
    """
    return (
        not expression.startswith("+")
        and not expression.startswith("*")
        and not expression.startswith("/")
    )


if __name__ == "__main__":
    constraints = [constraint1, constraint2, constraint3, constraint4]

    while True:
        expression = input("Enter the expression: ")
        result = True
        for i, constraint in enumerate(constraints):
            evaluation_result = constraint(expression)
            print(f"Constraint {i + 1}: {evaluation_result}")
            result = result and evaluation_result

        if result:
            print("The expression is valid.")
        else:
            print("The expression is invalid.")
