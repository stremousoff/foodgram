from users.validators import username_validator


class UsernameValidatorMixin:
    def validate_username(self, username):
        return username_validator(username)
