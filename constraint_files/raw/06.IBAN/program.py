def constraint1(iban: str) -> bool:
    """
    The length of the bank number shall be 22.
    """
    return len(iban) == 22


def constraint2(iban: str) -> bool:
    """
    The first 4 numbers of the bank number shall be: 1210 (CA).
    """
    return iban.startswith("1210")


def constraint3(iban: str) -> bool:
    """
    The next 2 numbers after the first 4 numbers shall be 00.
    """
    if len(iban) >= 6:
        return iban[4:6] == "00"
    return False


if __name__ == "__main__":
    iban = input("Enter your IBAN: ")

    if constraint1(iban) and constraint2(iban) and constraint3(iban):
        print("The IBAN is valid.")
    else:
        print("The IBAN is invalid.")
