from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.transaction import atomic
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from api.config import Error
from api.constants import Config
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from users.models import Subscription

User = get_user_model()


class FoodGramUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        model = User
        fields = UserSerializer.Meta.fields + ('is_subscribed', 'avatar')
        read_only_fields = fields

    def get_is_subscribed(self, user):
        user_request = self.context['request'].user
        return (
                user_request.is_authenticated
                and user_request.follower.filter(author=user).exists()
        )


class AvatarSerializer(UserSerializer):
    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ('avatar',)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug',)


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class CreateRecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        required=True
    )
    amount = serializers.IntegerField(
        required=True,
        min_value=Config.AMOUNT_MIN_VALUE,
        max_value=Config.AMOUNT_MAX_VALUE
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class UpdateCreateRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=True, allow_null=False,
                             allow_empty_file=False)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        allow_empty=False
    )
    author = FoodGramUserSerializer(read_only=True)
    ingredients = CreateRecipeIngredientSerializer(many=True,
                                                   allow_empty=False)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'name', 'image',
                  'text', 'cooking_time')
        read_only_fields = ('author', 'id')

    @staticmethod
    def _create_recipe_ingredients(recipe, ingredients):
        RecipeIngredient.objects.bulk_create(
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            ) for ingredient in ingredients
        )

    @atomic
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(author=self.context['request'].user,
                                       **validated_data)
        recipe.tags.set(tags)

        self._create_recipe_ingredients(recipe, ingredients)
        return recipe

    @atomic
    def update(self, recipe, validated_data):
        ingredients = validated_data.pop('ingredients', [])
        recipe.ingredients.clear()
        self._create_recipe_ingredients(recipe, ingredients)

        tags = validated_data.pop('tags', [])
        recipe.tags.set(tags)

        return super().update(recipe, validated_data)

    @staticmethod
    def validate_tags(tags):
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError(Error.UNIQUE_TAGS)
        return tags

    @staticmethod
    def validate_ingredients(ingredients):
        if len(set(ingredient['id'] for ingredient in ingredients)) != len(
                ingredients):
            raise serializers.ValidationError(Error.UNIQUE_INGREDIENTS)
        return ingredients

    def to_representation(self, recipe):
        return GetRecipeSerializer(recipe, context=self.context).data


class GetRecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True, source='ingredient.id')
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')
        read_only_fields = fields


class GetRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    tags = TagSerializer(many=True)
    author = FoodGramUserSerializer()
    ingredients = GetRecipeIngredientSerializer(
        many=True,
        source='recipeingredient_set'
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')
        read_only_fields = fields

    @staticmethod
    def _check_object_exists(context, recipe, model):
        user = context['request'].user
        return (
            user.is_authenticated
            and model.objects.filter(user=user, recipe=recipe).exists()
        )

    def get_is_favorited(self, recipe):
        return self._check_object_exists(self.context, recipe, Favorite)

    def get_is_in_shopping_cart(self, recipe):
        return self._check_object_exists(self.context, recipe, ShoppingCart)


class RecipeShortSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionsListSerializer(FoodGramUserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(default=0)

    class Meta(FoodGramUserSerializer.Meta):
        fields = FoodGramUserSerializer.Meta.fields + (
            'recipes', 'recipes_count'
        )
        read_only_fields = fields

    def get_recipes(self, user):
        recipes = user.recipes.all()
        recipes_limit = self.context['request'].query_params.get(
            'recipes_limit')
        if recipes_limit:
            try:
                recipes = recipes[:int(recipes_limit)]
            except ValueError:
                pass
        return RecipeShortSerializer(
            recipes, many=True, context=self.context
        ).data


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ('user', 'author')
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('user', 'author')
            ),
        ]

    def validate(self, data):
        if data['user'] == data['author']:
            raise serializers.ValidationError(
                Error.SUBSCRIPTION_YOURSELF
            )
        return data

    def to_representation(self, instance):
        return SubscriptionsListSerializer(instance.author,
                                           context=self.context).data


class ShoppingCartFavoriteBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = None
        fields = ('user', 'recipe')

    def validate(self, data):
        model = self.Meta.model
        if model.objects.filter(
                user=data['user'],
                recipe=data['recipe']
        ).exists():
            raise serializers.ValidationError(
                Error.ALREADY_ADDED.format(model.__name__)
            )
        return data

    def to_representation(self, instance):
        return RecipeShortSerializer(instance.recipe).data


class FavoriteSerializer(ShoppingCartFavoriteBaseSerializer):
    class Meta(ShoppingCartFavoriteBaseSerializer.Meta):
        model = Favorite


class ShoppingCartSerializer(ShoppingCartFavoriteBaseSerializer):
    class Meta(ShoppingCartFavoriteBaseSerializer.Meta):
        model = ShoppingCart
