def constraint1(url: str) -> bool:
    """
    The url shall start with either http:// or https://.
    """
    return url.startswith("http://") or url.startswith("https://")


def constraint2(url: str) -> bool:
    """
    The url shall not contain any spaces.
    """
    return " " not in url


def constraint3(url: str) -> bool:
    """
    The url shall contain at least one dot character (.).
    """
    return "." in url


if __name__ == "__main__":
    url = input("Enter your url: ")

    if constraint1(url) and constraint2(url) and constraint3(url):
        print("The url is valid.")
    else:
        print("The url is invalid.")
