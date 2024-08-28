from django.contrib import admin
from django.contrib.auth.models import Group
from django.utils.safestring import mark_safe

from recipes.constants import Config
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 0
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('image_display', 'name', 'author', 'short_text',
                    'ingredients_list', 'tags_list', 'favorites_count')
    list_filter = ('author',)
    filter_horizontal = ('ingredients',)
    inlines = (RecipeIngredientInline, )

    @admin.display(description='Изображение')
    def image_display(self, recipe):
        return mark_safe(
            f'<img src={recipe.image.url} width="60" height="60">'
        )

    @staticmethod
    @admin.display(description='Описание')
    def short_text(recipe):
        return recipe.text[:Config.LENGTH_ON_STR]

    @admin.display(description='Ингредиенты')
    def ingredients_list(self, recipe):
        return ', '.join(
            f'{ingredient_in_recipe.ingredient.name} '
            f'({ingredient_in_recipe.amount}/'
            f'{ingredient_in_recipe.ingredient.measurement_unit})'
            for ingredient_in_recipe in recipe.recipeingredient_set.all())

    @admin.display(description='Теги')
    def tags_list(self, recipe):
        return ', '.join(
            tag_in_recipe.name for tag_in_recipe in recipe.tags.all()
        )

    @admin.display(description='В избранном раз')
    def favorites_count(self, recipe):
        return recipe.favorite_set.count()


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')


@admin.register(Favorite)
class UserRecipeAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    unique_together = ('user', 'recipe')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    unique_together = ('user', 'recipe')


admin.site.unregister(Group)
