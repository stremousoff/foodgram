from django.contrib import admin
from django.utils.safestring import mark_safe

from recipes.models import (
    Ingredient, Recipe, RecipeIngredient, ShoppingCart, Tag, Favorite
)

from users.models import Subscription


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 0
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('image_display', 'name', 'author', 'short_text')
    list_filter = ('author',)
    filter_horizontal = ('ingredients',)
    inlines = (RecipeIngredientInline, )

    @admin.display(description='Картинка рецепта')
    def image_display(self, recipe):
        if recipe.image:
            return mark_safe(
                f'<img src={recipe.image.url} width="60" height="60">'
            )

    @staticmethod
    @admin.display(description='Описание рецепта')
    def short_text(recipe):
        return recipe.text


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'follower')


@admin.register(Favorite)
class UserRecipeAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    unique_together = ('user', 'recipe')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    unique_together = ('user', 'recipe')
