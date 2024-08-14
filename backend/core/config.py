class Config:
    # Кол-во показываемых символов методом __str__()

    LENGTH_ON_STR = 15

    # Сообщения об ошибках
    USERNAME_FAILED = 'Имя пользователя `{username}` недопустимо.'
    USERNAME_OR_EMAIL_EXIST = 'Значение `{}` уже занято.'
    TOKEN_ERROR = 'Поле `confirmation_code` некорректно.'
    PERMISSION_DENIED = 'Недостаточно прав для выполнения действия.'
    USER_DELETED = 'Пользователь `{user}` удален.'
    USERNAME_ERROR = (
        'Поле `username` должно содержать только буквы, цифры и символы: '
        '`@`, `.`, `+`, `-`, `_`. Сейчас оно содержит недопустимые '
        'символы: {wrong_symbols}.'
    )
    PATTERN_USERNAME = r'^[\\w.@+-]+$'

    # Настройки модели Users
    USERNAME_MAX_LENGTH = 150
    EMAIL_MAX_LENGTH = 254
    FIRST_NAME_MAX_LENGTH = 150
    LAST_NAME_MAX_LENGTH = 150
    PASSWORD_MAX_LENGTH = 20
    DIRECTORY_AVATAR = 'users/'
