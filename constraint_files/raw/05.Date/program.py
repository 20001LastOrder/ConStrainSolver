def constraint1(date: str) -> bool:
    """
    The date shall contain two hyphens.
    """
    return date.count("-") == 2


def constraint2(date: str) -> bool:
    """
    If there are at least one hyphen, the part before the first hyphen shall be a number between 0 and 2025.
    """
    if "-" in date:
        part = date.split("-")[0]
        return part.isdigit() and 0 <= int(part) <= 2025
    return True


def constraint3(date: str) -> bool:
    """
    If there are at least two hyphens, the part after the first hyphen but before the second hyphen shall be a number between 1 and 12.
    """
    if date.count("-") >= 2:
        part = date.split("-")[1]
        return part.isdigit() and 1 <= int(part) <= 12
    return True


def constraint4(date: str) -> bool:
    """
    If there are at least two hyphen, The part after the second hyphen shall be a number between 1 and 31.
    """
    if date.count("-") >= 2:
        part = date.split("-", 2)[2]
        return part.isdigit() and 1 <= int(part) <= 31
    return True


if __name__ == "__main__":
    constraints = [constraint1, constraint2, constraint3, constraint4]
    while True:
        date = input("Enter the date: ")
        result = True
        for i, constraint in enumerate(constraints):
            evaluation_result = constraint(date)
            print(f"Constraint {i + 1}: {evaluation_result}")
            result = result and evaluation_result

        if result:
            print("The date is valid.")
        else:
            print("The date is invalid.")
