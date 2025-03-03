def constraint1(dna: str) -> bool:
    """
    The DNA sequence shall only contain letters "A", "T", "C" and "G".
    """
    return all(char in "ATCG" for char in dna)


def constraint2(dna: str) -> bool:
    """
    The length of The DNA sequence shall be at least 10.
    """
    return len(dna) >= 10


def constraint3(dna: str) -> bool:
    """
    The length of The DNA sequence shall be a multiple of three.
    """
    return len(dna) % 3 == 0


def constraint4(dna: str) -> bool:
    """
    The DNA sequence shall starts with "ATG".
    """
    return dna.startswith("ATG")


def constraint5(dna: str) -> bool:
    """
    The DNA sequence shall end with one of the following strings: "TAA", "TAG" or "TGA".
    """
    return dna.endswith("TAA") or dna.endswith("TAG") or dna.endswith("TGA")


if __name__ == "__main__":
    constraints = [constraint1, constraint2, constraint3, constraint4, constraint5]
    while True:
        dna = input("Enter the dna: ")
        result = True
        for i, constraint in enumerate(constraints):
            evaluation_result = constraint(dna)
            print(f"Constraint {i + 1}: {evaluation_result}")
            result = result and evaluation_result

        if result:
            print("The dna is valid.")
        else:
            print("The dna is invalid.")
