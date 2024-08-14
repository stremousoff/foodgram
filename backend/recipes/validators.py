from rest_framework.exceptions import ValidationError


def cooking_time_validator(value):
    if value < 1:
        raise ValidationError(
            'Время приготовления должно быть не менее 1(одной) минуты.'
        )
