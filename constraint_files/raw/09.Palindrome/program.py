def constraint1(palindrome: str) -> bool:
    """
    A palindrome shall be at least 3 characters long
    """
    return len(palindrome) >= 3


def constraint2(palindrome: str) -> bool:
    """
    A palindrome shall be identical to its reverse
    """
    return palindrome == palindrome[::-1]


if __name__ == "__main__":
    palindrome = input("Enter the palindrome: ")

    if constraint1(palindrome) and constraint2(palindrome):
        print("The palindrome is valid.")
    else:
        print("The palindrome is invalid.")
