import re


# TODO: we need a prettifier that can take non-US numbers
def pretty_print_phone_number(number: str) -> str:
    """E.164 number to prettified +1 (xxx) xxx xxxx"""
    country_code, area_code, three, four = (
        number[0:2],
        number[2:5],
        number[5:8],
        number[8:],
    )
    return f"{country_code} ({area_code}) {three} {four}"


class InvalidUSPhoneNumberException(Exception):
    pass


def e164_format_phone_number(value: str) -> str:
    """
    any number to E.164
    """
    value = value.strip()

    # get only the digits out
    numbers = "".join([c for c in value if c.isdigit()])

    if value[:2] == "+1" and len(numbers) != 11:
        raise InvalidUSPhoneNumberException

    if len(numbers) == 11:
        if numbers[0] == "1":
            return f"+{numbers}"
        raise InvalidUSPhoneNumberException

    elif len(numbers) == 10:
        return f"+1{numbers}"

    else:
        raise InvalidUSPhoneNumberException


def to_snake_case(string):
    return "_".join([s.strip() for s in string.strip().lower().split(" ")])


first_cap_re = re.compile("(.)([A-Z][a-z]+)")
all_cap_re = re.compile("([a-z0-9])([A-Z])")


def camel_to_snake(name):
    s1 = first_cap_re.sub(r"\1_\2", name)
    return all_cap_re.sub(r"\1_\2", s1).lower()
