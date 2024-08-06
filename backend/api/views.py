import os

from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from djoser.serializers import UserSerializer
from djoser.views import UserViewSet
from rest_framework import status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .filters import IngredientFilter, RecipeFilter
from .serializers import (AvatarSerializer, TagSerializer,
                          IngredientSerializer, RecipeSerializerGet,
                          RecipeSerializerPost)
from recipes.models import Tag, Ingredient, Recipe, UserRecipe, ShoppingCart

User = get_user_model()


class UserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=False, methods=['get'], url_path='users/subscriptions')
    def get_subscriptions(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class AvatarView(APIView):
    serializer_class = AvatarSerializer
    queryset = User.objects.all()

    @staticmethod
    def put(request):
        user = User.objects.get(username=request.user.username)
        if user.avatar:
            path_image_avatar = user.avatar.path
            os.remove(path_image_avatar)
        serializer = AvatarSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def delete(request):
        user = User.objects.get(username=request.user.username)
        if user.avatar:
            user.avatar.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(ReadOnlyModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeSerializerGet
        return RecipeSerializerPost

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, pk=None):
        recipe = Recipe.objects.get(id=pk)
        user = request.user
        favourite, _ = UserRecipe.objects.get_or_create(user=user, recipe=recipe)
        if request.method == 'POST':
            favourite.save()
            return Response(
                {'message': 'Рецепт добавлен в избранное'},
                status=status.HTTP_201_CREATED
            )
        favourite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'])
    def shopping_cart(self, request, pk=None):
        recipe = Recipe.objects.get(id=pk)
        user = request.user
        cart, _ = ShoppingCart.objects.get_or_create(user=user, recipe=recipe)
        if request.method == 'POST':
            cart.save()
            return Response(
                {'message': 'Рецепт добавлен в список покупок'},
                status=status.HTTP_201_CREATED
            )
        cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


