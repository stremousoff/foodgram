import re

from rest_framework.exceptions import ValidationError


def username_validator(username):
    if not re.match('^[\\w.@+-]+$', username):
        raise ValidationError('Invalid username')
    return username
