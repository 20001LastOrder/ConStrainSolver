def constraint1(isbn: str) -> bool:
    """
    The ISBN shall include digits (0–9) , the letter "X", or hyphens.
    """
    return all(char.isdigit() or char in "X-" for char in isbn)


def constraint2(isbn: str) -> bool:
    """
    The last character of the ISBN shall either be digits (0-9) or the letter "X".
    """
    if len(isbn) == 0:
        return False
    return isbn[-1].isdigit() or isbn[-1] == "X"


def constraint3(isbn: str) -> bool:
    """
    The ISBN shall contain exactly 10 characters excluding hyphens.
    """
    return len(isbn.replace("-", "")) == 10


def constraint4(isbn: str) -> bool:
    """
    Hyphens shall not be at the beginning of the ISBN.
    """
    return not isbn.startswith("-")


def constraint5(isbn: str) -> bool:
    """
    Hyphens shall not occur consecutively in the ISBN.
    """
    return "--" not in isbn


def constraint6(isbn: str) -> bool:
    """
    An ISBN shall contain at most 3 hyphens
    """
    return isbn.count("-") <= 3


if __name__ == "__main__":
    constraints = [constraint1, constraint2, constraint3, constraint4, constraint5, constraint6]

    while True:
        isbn = input("Enter the ISBN: ")
        result = True
        for i, constraint in enumerate(constraints):
            evaluation_result = constraint(isbn)
            print(f"Constraint {i + 1}: {evaluation_result}")
            result = result and evaluation_result

        if (
            constraint1(isbn)
            and constraint2(isbn)
            and constraint3(isbn)
            and constraint4(isbn)
            and constraint5(isbn)
            and constraint6(isbn)
        ):
            print("The ISBN is valid.")
        else:
            print("The ISBN is invalid.")
