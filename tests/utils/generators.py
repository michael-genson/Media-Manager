from datetime import datetime, timedelta
import random
import string


def random_string(length=10) -> str:
    return "".join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length)).strip()


def random_email(length=10) -> str:
    return "".join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length)) + "@example.com"


def random_password(length=20) -> str:
    return random_string(length)


def random_bool() -> bool:
    return bool(random.getrandbits(1))


def random_int(min=-4294967296, max=4294967296) -> int:
    return random.randint(min, max)


def random_url(https=True) -> str:
    """all random URLs are the same length, with or without https (25 characters)"""

    return f"{'https' if https else 'http'}://{random_string(5 if https else 6)}.example.com"


def random_datetime(start: datetime | None = None, end: datetime | None = None) -> datetime:
    """
    A random datetime between two datetimes

    Defaults to a year ago through now
    """

    start = start or (datetime.now() - timedelta(days=365))
    end = end or datetime.now()

    delta_max = (start - end).microseconds
    return end - timedelta(microseconds=random_int(delta_max))
