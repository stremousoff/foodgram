from django_filters import rest_framework as filters

from recipes.models import Ingredient, Recipe, Tag


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(filters.FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        queryset=Tag.objects.all(),
        to_field_name='slug'
    )
    is_in_shopping_cart = filters.BooleanFilter(method='filter_recipes')
    is_favorited = filters.BooleanFilter(method='filter_recipes')

    class Meta:
        model = Recipe
        fields = ('tags', 'is_in_shopping_cart', 'is_favorited', 'author')

    def filter_recipes(self, queryset, name, value):
        filters_map = {
            'is_in_shopping_cart': 'shoppingcart__user',
            'is_favorited': 'favorite__user'
        }
        filter_field = filters_map[name]
        return (
            queryset.filter(**{filter_field: self.request.user})
            if self.request.user.is_authenticated and value
            else queryset
        )
