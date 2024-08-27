from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.db.models import F, Q

from users.constants import Config


class FoodGramUser(AbstractUser):
    REQUIRED_FIELDS = ('first_name', 'last_name', 'username')
    USERNAME_FIELD = 'email'

    email = models.EmailField(
        Config.EMAIL,
        max_length=Config.EMAIL_MAX_LENGTH,
        unique=True,
    )
    username = models.CharField(
        Config.USERNAME,
        max_length=Config.USERNAME_MAX_LENGTH,
        validators=(UnicodeUsernameValidator(),),
        unique=True,
    )
    first_name = models.CharField(
        Config.FIRST_NAME,
        max_length=Config.FIRST_NAME_MAX_LENGTH,
    )
    last_name = models.CharField(
        Config.LAST_NAME,
        max_length=Config.LAST_NAME_MAX_LENGTH,
    )
    avatar = models.ImageField(
        Config.AVATAR,
        upload_to=Config.DIRECTORY_AVATAR,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = Config.USER
        verbose_name_plural = Config.USERS
        ordering = ('username',)

    def __str__(self):
        return self.username[:Config.LENGTH_ON_STR]


class Subscription(models.Model):
    user = models.ForeignKey(
        FoodGramUser,
        on_delete=models.CASCADE,
        verbose_name=Config.FOLLOWER,
        related_name='follower',

    )
    author = models.ForeignKey(
        FoodGramUser,
        on_delete=models.CASCADE,
        verbose_name=Config.USERNAME,
        related_name='following',
    )

    class Meta:
        verbose_name = Config.SUBSCRIPTION
        verbose_name_plural = Config.SUBSCRIPTIONS
        ordering = ('user',)
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='subscription_exists'
            ),
            models.CheckConstraint(
                check=~Q(user_id=F('author_id')),
                name='no_self_following'
            )
        ]

    def __str__(self):
        return f'{self.user} --> {self.author}'
