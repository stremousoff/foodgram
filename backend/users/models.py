from django.contrib.auth.models import AbstractUser
from django.db import models

from core.config import Config
from users.validators import username_validator


class FoodGramUser(AbstractUser):
    email = models.EmailField(max_length=Config.EMAIL_MAX_LENGTH, unique=True)
    username = models.CharField(max_length=Config.USERNAME_MAX_LENGTH,
                                unique=True, validators=(username_validator,))
    first_name = models.CharField(max_length=Config.FIRST_NAME_MAX_LENGTH)
    last_name = models.CharField(max_length=Config.LAST_NAME_MAX_LENGTH)
    password = models.CharField(max_length=Config.PASSWORD_MAX_LENGTH)
    avatar = models.ImageField(upload_to=Config.DIRECTORY_AVATAR, null=True)

    class Meta(AbstractUser.Meta):
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username[:Config.LENGTH_ON_STR]
