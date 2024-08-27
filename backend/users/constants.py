class Config:
    # Кол-во показываемых символов методом __str__()
    LENGTH_ON_STR = 15

    # Настройки модели Users
    USERNAME_MAX_LENGTH = 150
    EMAIL_MAX_LENGTH = 254
    FIRST_NAME_MAX_LENGTH = 150
    LAST_NAME_MAX_LENGTH = 150
    DIRECTORY_AVATAR = 'users/'

    # Verbose name
    USERNAME = 'Никнейм'
    EMAIL = 'Адрес электронной почты'
    FIRST_NAME = 'Имя'
    LAST_NAME = 'Фамилия'
    AVATAR = 'Аватар пользователя'
    FOLLOWER = 'Подписан'
    FOODGRAM_USER = 'Пользователь'

    # Verbose/plural для META
    USER = 'Пользователь'
    USERS = 'Пользователи'
    SUBSCRIPTION = 'Подписка'
    SUBSCRIPTIONS = 'Подписки'
