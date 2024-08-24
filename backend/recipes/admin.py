from django.contrib import admin
from django.contrib.auth.models import Group
from django.utils.safestring import mark_safe

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 0
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('image_display', 'name', 'author', 'short_text',
                    'ingredients_list', 'tags_list')
    list_filter = ('author',)
    filter_horizontal = ('ingredients',)
    inlines = (RecipeIngredientInline, )

    @admin.display(description='Картинка рецепта')
    def image_display(self, recipe):
        return mark_safe(
            f'<img src={recipe.image.url} width="60" height="60">'
        )

    @staticmethod
    @admin.display(description='Описание рецепта')
    def short_text(recipe):
        return recipe.text

    @admin.display(description='Ингредиенты')
    def ingredients_list(self, recipe):
        return ', '.join(
            f'{i.ingredient.name} ({i.amount} {i.ingredient.measurement_unit})'
            for i in recipe.recipeingredient_set.all())

    @admin.display(description='Теги')
    def tags_list(self, recipe):
        return ', '.join(t.name for t in recipe.tags.all())


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
