import random
import string

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q, F

from recipes.validators import cooking_time_validator

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(
        max_length=128,
        verbose_name='Название ингредиента'
    )
    measurement_unit = models.CharField(
        max_length=64,
        verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=32, unique=True, verbose_name='Тег')
    slug = models.SlugField(max_length=32, unique=True, verbose_name='Слаг')

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиенты',
    )
    name = models.CharField(
        max_length=256,
        verbose_name='Название рецепта',
        unique=True
    )
    image = models.ImageField(
        upload_to='recipes/',
        verbose_name='Изображение',
        null=True,
        blank=True
    )
    text = models.TextField(verbose_name='Описание рецепта')
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=[cooking_time_validator]
    )
    short_url = models.CharField(
        max_length=6,
        unique=True,
        null=True,
        blank=True
    )

    def save(self, *args, **kwargs):
        if not self.short_url:
            self.short_url = ''.join(
                random.choices(string.ascii_letters + string.digits, k=4)
            )
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return f'{self.short_url}'

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('name',)

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        default=1
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        ordering = ('recipe',)

    def __str__(self):
        return f'{self.recipe} - {self.ingredient}'


class UserRecipe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Рецепт пользователя'
        verbose_name_plural = 'Рецепты пользователя'
        ordering = ('user',)

    def __str__(self):
        return f'{self.user} - {self.recipe}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        ordering = ('user',)

    def __str__(self):
        return f'{self.user} - {self.recipe}'


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписан на:'
    )

    class Meta:
        verbose_name = 'Подписчик'
        verbose_name_plural = 'Подписчики'
        ordering = ('user',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'follower'],
                name='должна быть уникальная подписка'
            ),
            models.CheckConstraint(
                check=~Q(user_id=F('follower_id')),
                name='нельзя подписаться на себя'
            )
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.follower}'
