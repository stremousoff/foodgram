import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from djoser.serializers import UserSerializer, UserCreateSerializer
from rest_framework import serializers

from recipes.models import Tag, Ingredient, Recipe, RecipeIngredient, \
    UserRecipe, ShoppingCart

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return data


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'password')
        read_only_fields = ('id',)


class CustomUserDetailSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'avatar')


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ('avatar',)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class RecipeIngredientSerializer(serializers.ModelSerializer):
    recipe = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all(),
        source='id'
    )
    ingredient = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient_id'
    )

    class Meta:
        model = RecipeIngredient
        fields = '__all__'


class RecipeSerializerPost(serializers.ModelSerializer):
    image = Base64ImageField(required=False, allow_null=True)
    author = UserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = ('name', 'tags', 'ingredients', 'cooking_time', 'text',
                  'image', 'author')
        read_only_fields = ('author',)

    def create(self, validated_data):
        ingredients = self.initial_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)

        for ingredient in ingredients:
            amount = ingredient['amount']
            ingredient = Ingredient.objects.get(id=ingredient['id'])
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                amount=amount
            )
        return recipe


class RecipeSerializerGet(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = CustomUserDetailSerializer()
    ingredients = IngredientSerializer(many=True,)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def get_is_favorited(self, recipe):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return True if UserRecipe.objects.filter(user=user, recipe=recipe).exists() else False

    def get_is_in_shopping_cart(self, recipe):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return True if ShoppingCart.objects.filter(user=user, recipe=recipe).exists() else False

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'name', 'is_favorited', 'is_in_shopping_cart', 'image', 'text', 'cooking_time')
        read_only_fields = (fields,)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        for ingredient in representation['ingredients']:
            ingredient['amount'] = RecipeIngredient.objects.get(
                recipe=instance, ingredient=ingredient['id']
            ).amount
        return representation
