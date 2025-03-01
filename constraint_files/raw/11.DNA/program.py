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
    dna = input("Enter the DNA sequence: ")

    if (
        constraint1(dna)
        and constraint2(dna)
        and constraint3(dna)
        and constraint4(dna)
        and constraint5(dna)
    ):
        print("The DNA sequence is valid.")
    else:
        print("The DNA sequence is invalid.")
