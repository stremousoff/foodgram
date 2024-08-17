from django.contrib.auth import get_user_model
from django.db.transaction import atomic
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from core.utils import Base64ImageField
from recipes.models import (Ingredient, Recipe, RecipeIngredient, ShoppingCart,
                            Subscription, Tag, UserRecipe)

User = get_user_model()


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'password')
        read_only_fields = ('id',)
        extra_kwargs = {
            'password': {'write_only': True},
        }


class CustomUserDetailSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'avatar')
        read_only_fields = fields

    def get_is_subscribed(self, user):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(
                user=user, follower=request.user).exists()
        return False


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


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        required=True
    )
    amount = serializers.IntegerField(required=True)

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                'Количество должно быть больше нуля'
            )
        return value

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeSerializerPost(serializers.ModelSerializer):
    image = Base64ImageField()
    tags = serializers.PrimaryKeyRelatedField(many=True,
                                              queryset=Tag.objects.all())
    author = CustomUserDetailSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')
        read_only_fields = ('author', 'id', 'is_favorited',
                            'is_in_shopping_cart')

    @atomic
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)

        recipe_ingredients = [
            RecipeIngredient(recipe=recipe, ingredient=ingredient['id'],
                             amount=ingredient['amount'])
            for ingredient in ingredients
        ]

        RecipeIngredient.objects.bulk_create(recipe_ingredients)
        return recipe

    @atomic
    def update(self, recipe, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe.tags.set(tags)
        recipe.ingredients.clear()
        recipe_ingredients = [
            RecipeIngredient(recipe=recipe, ingredient=ingredient['id'],
                             amount=ingredient['amount'])
            for ingredient in ingredients
        ]
        RecipeIngredient.objects.bulk_create(recipe_ingredients)
        return super().update(recipe, validated_data)

    @staticmethod
    def check_object_exists(context, recipe, model):
        user = context.get('request').user
        return True if model.objects.filter(user=user,
                                            recipe=recipe).exists() else False

    def get_is_favorited(self, recipe):
        return self.check_object_exists(self.context, recipe, UserRecipe)

    def get_is_in_shopping_cart(self, recipe):
        return self.check_object_exists(self.context, recipe, ShoppingCart)

    def validate_tags(self, tags):
        if not tags:
            raise serializers.ValidationError(
                'Необходимо добавить хотя бы один тег для рецепта.'
            )
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError(
                'Все теги должны быть разными.'
            )
        return tags

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise serializers.ValidationError(
                'Необходимо добавить хотя бы один ингредиент для рецепта.'
            )
        if len(set(ingredient['id'] for ingredient in ingredients)) != len(
                ingredients):
            raise serializers.ValidationError(
                'Ингредиенты должны быть разными.'
            )
        return ingredients

    def validate_image(self, image):
        if not image:
            raise serializers.ValidationError(
                'Поле image не может быть пустым.'
            )
        return image

    def to_representation(self, recipe):
        representation = super().to_representation(recipe)
        representation['tags'] = TagSerializer(recipe.tags, many=True).data
        ingredients = [
            {
                'id': ingredient_for_recipe.ingredient.id,
                'name': ingredient_for_recipe.ingredient.name,
                'measurement_unit': ingredient_for_recipe.ingredient
                .measurement_unit,
                'amount': ingredient_for_recipe.amount
            } for ingredient_for_recipe in RecipeIngredient.objects.filter(
                recipe=recipe
            )
        ]
        representation['ingredients'] = ingredients
        return representation


class RecipeSerializerGet(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = CustomUserDetailSerializer()
    ingredients = IngredientSerializer(many=True,)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    @staticmethod
    def check_object_exists(context, recipe, model):
        user = context.get('request').user
        if user.is_anonymous:
            return False
        return True if model.objects.filter(user=user,
                                            recipe=recipe).exists() else False

    def get_is_favorited(self, recipe):
        return self.check_object_exists(self.context, recipe, UserRecipe)

    def get_is_in_shopping_cart(self, recipe):
        return self.check_object_exists(self.context, recipe, ShoppingCart)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')
        read_only_fields = (fields,)

    def to_representation(self, recipe):
        representation = super().to_representation(recipe)
        for ingredient in representation['ingredients']:
            ingredient['amount'] = RecipeIngredient.objects.get(
                recipe=recipe, ingredient=ingredient['id']
            ).amount
        return representation


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ('user', 'follower')
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('user', 'follower')
            ),
        ]

    def validate(self, data):
        if data['user'] == data['follower']:
            raise serializers.ValidationError(
                'Нельзя подписаться самому на себя.'
            )
        return data


class RecipeShortSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionsListSerializer(CustomUserDetailSerializer):
    recipes = RecipeShortSerializer(many=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta(CustomUserDetailSerializer.Meta):
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count', 'avatar')

    @staticmethod
    def get_recipes_count(user):
        return user.recipes.count()

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        limit_recipe = self.context['request'].query_params.get(
            'recipes_limit'
        )
        if limit_recipe:
            representation['recipes'] = (
                representation['recipes'][:int(limit_recipe)]
            )
        return representation
