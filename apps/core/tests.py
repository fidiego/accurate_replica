from core.formatters import e164_format_phone_number, InvalidUSPhoneNumberException
from core.formatters import pretty_print_phone_number


def test_e164_formatter__should_pass():
    numbers = [
        "+1 321 555 0123",
        "+1 (321) 555-0123",
        "+1 (321) 555 0123",
        "(321) 555 0123",
        "321.555.0123",
        "3215550123",
        "+1   321   55  5 0  123",
        "1   321   55  5 0  123",
    ]

    for number in numbers:
        formatted = e164_format_phone_number(number)

        assert len(formatted) == 12  # test for correct length
        assert formatted[:2] == "+1"  # test for correct prefix


def test_e164_formatter__should_not_pass():
    numbers = ["+1321555012", "+132155501234", "321555012", "32155501234"]

    for number in numbers:
        try:
            formatted = e164_format_phone_number(number)
            assert (
                False
            )  # this case is only reached if the formatter does not raise an exception
        except InvalidUSPhoneNumberException as e:
            assert True


def test_pretty_print_phone_number():
    numbers = [
        "+1 321 555 0123",
        "+1 (321) 555-0123",
        "+1 (321) 555 0123",
        "(321) 555 0123",
        "321.555.0123",
        "3215550123",
        "+1   321   55  5 0  123",
        "1   321   55  5 0  123",
    ]

    for number in numbers:
        assert (
            pretty_print_phone_number(e164_format_phone_number(number))
            == "+1 (321) 555 0123"
        )
