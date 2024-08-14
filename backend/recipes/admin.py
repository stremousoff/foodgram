from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Recipe, Tag, Ingredient


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('image_display', 'name', 'author', 'short_text')
    list_filter = ('author',)

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
