from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint

from .constants import Config
from .core import generate_short_url

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(
        Config.NAME_INGREDIENT,
        max_length=Config.INGREDIENT_MAX_LENGTH,
    )
    measurement_unit = models.CharField(
        Config.MEASUREMENT_UNIT,
        max_length=Config.MEASUREMENT_MAX_LENGTH,
    )

    class Meta:
        verbose_name = Config.INGREDIENT
        verbose_name_plural = Config.INGREDIENTS
        ordering = ('name',)
        constraints = (
            UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='name_and_measurement_unit_unique'
            ),
        )

    def __str__(self):
        return self.name[:Config.LENGTH_ON_STR]


class Tag(models.Model):
    name = models.CharField(
        Config.NAME_TAG,
        max_length=Config.TAG_MAX_LENGTH,
        unique=True,
    )
    slug = models.SlugField(
        Config.SLUG_TAG,
        max_length=Config.SLUG_MAX_LENGTH,
        unique=True,
    )

    class Meta:
        verbose_name = Config.TAG
        verbose_name_plural = Config.TAGS
        ordering = ('name',)
        constraints = (
            UniqueConstraint(
                fields=('name', 'slug'),
                name='name_and_slug_unique'
            ),
        )

    def __str__(self):
        return self.name[:Config.LENGTH_ON_STR]


class Recipe(models.Model):
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name=Config.NAME_TAG,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name=Config.AUTHOR
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name=Config.NAME_INGREDIENT,
    )
    name = models.CharField(
        Config.NAME_RECIPE,
        max_length=Config.NAME_RECIPE_MAX_LENGTH,
        unique=True
    )
    image = models.ImageField(
        Config.IMAGE_RECIPE,
        upload_to=Config.DIRECTORY_RECIPE,
    )
    text = models.TextField(Config.TEXT_RECIPE)
    cooking_time = models.PositiveSmallIntegerField(
        Config.COOKING_TIME,
        validators=(
            MinValueValidator(
                limit_value=Config.MIN_COOKING_TIME,
                message=Config.MIN_COOKING_TIME_ERROR
            ),
            MaxValueValidator(
                limit_value=Config.MAX_COOKING_TIME,
                message=Config.MAX_COOKING_TIME_ERROR
            )
        )
    )
    short_url = models.CharField(
        Config.SHORT_URL,
        max_length=Config.MAX_URL_LENGTH,
        unique=True,
    )
    add_time = models.DateTimeField(
        Config.ADD_TIME,
        auto_now_add=True
    )

    class Meta:
        verbose_name = Config.RECIPE
        verbose_name_plural = Config.RECIPES
        ordering = ('-add_time',)

    def save(self, *args, **kwargs):
        if not self.short_url:
            self.short_url = generate_short_url()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return f'{self.short_url}'

    def __str__(self):
        return self.name[:Config.LENGTH_ON_STR]


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name=Config.NAME_RECIPE
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name=Config.NAME_INGREDIENT
    )
    amount = models.PositiveSmallIntegerField(
        Config.AMOUNT,
        validators=(
            MinValueValidator(
                limit_value=Config.MIN_INGREDIENT_AMOUNT,
                message=Config.MIN_INGREDIENT_AMOUNT_ERROR
            ),
            MaxValueValidator(
                limit_value=Config.MAX_INGREDIENT_AMOUNT,
                message=Config.MAX_INGREDIENT_AMOUNT_ERROR
            )
        )
    )

    class Meta:
        verbose_name = Config.INGREDIENT_RECIPE
        verbose_name_plural = Config.INGREDIENTS_RECIPE
        ordering = ('recipe',)
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='recipe_ingredient_unique'
            ),
        )

    def __str__(self):
        return (f'{self.ingredient.name[:Config.LENGTH_ON_STR]} -> '
                f'{self.recipe.name[:Config.LENGTH_ON_STR]}')


class UserRecipe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=Config.USER,
        related_name='%(class)s'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name=Config.NAME_RECIPE
    )

    class Meta:
        abstract = True
        ordering = ('user',)
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='%(class)s_unique'
            ),
        )

    def __str__(self):
        return (f'{self.recipe[:Config.LENGTH_ON_STR]} -> '
                f'{self.user[:Config.LENGTH_ON_STR]}')


class Favorite(UserRecipe):
    class Meta(UserRecipe.Meta):
        verbose_name = Config.FAVORITED_RECIPE
        verbose_name_plural = Config.FAVORITED_RECIPES


class ShoppingCart(UserRecipe):
    class Meta(UserRecipe.Meta):
        verbose_name = Config.SHOPPING_CART
        verbose_name_plural = Config.SHOPPING_CART
