from django.utils import timezone
from datetime import datetime

import string
import random

def get_random_string(length, include_letters=False):
    characters = (
        string.digits if not include_letters else string.ascii_letters + string.digits
    )
    result_str = "".join(random.choice(characters) for i in range(length))
    return result_str


def get_random_password(length):
    characters = string.ascii_letters + string.digits
    simbols = "#$%&/()=?¡¿!-_:*+"
    result_str = "".join(random.choice(characters) for i in range(length - 2))
    result_str += "".join(random.choice(simbols) for i in range(2))
    return result_str

def get_date_with_timezone(date):
    return timezone.make_aware(date, timezone.get_default_timezone())

