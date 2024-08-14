from django.contrib.auth import get_user_model
from django.http import FileResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import (
    AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from recipes.models import (Ingredient, Recipe, ShoppingCart, Subscription,
                            Tag, UserRecipe)

from .filters import IngredientFilter, RecipeFilter
from .permissions import OwnerAdminOrReadOnly
from .serializers import (
    AvatarSerializer, IngredientSerializer, RecipeSerializerGet,
    RecipeSerializerPost, SubscriptionsListSerializer, TagSerializer,
    CustomUserDetailSerializer, SubscriptionSerializer
)

User = get_user_model()


class UserFoodgramViewSet(UserViewSet):
    queryset = User.objects.all()
    pagination_class = LimitOffsetPagination

    def list(self, request, *args, **kwargs):
        users = self.get_queryset()
        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(users, request)
        serializer = CustomUserDetailSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    @action(detail=False, url_path='me',
            permission_classes=[IsAuthenticated, ])
    def me(self, request):
        serializer = CustomUserDetailSerializer(
            get_object_or_404(User, username=request.user),
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['put', 'delete'], url_path='me/avatar',
            permission_classes=[IsAuthenticated, ])
    def avatar(self, request):
        user = User.objects.get(username=request.user.username)
        if request.method == 'PUT':
            if user.avatar:
                user.avatar.delete()
            serializer = AvatarSerializer(user, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        if user.avatar:
            user.avatar.delete()
        user.avatar.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, url_path='subscriptions',
            serializer_class=SubscriptionsListSerializer,
            permission_classes=[OwnerAdminOrReadOnly, ])
    def subscriptions(self, request):
        following = Subscription.objects.filter(follower=request.user)
        users = [User.objects.get(id=user.user_id) for user in following]
        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(users, request)
        serializer = self.get_serializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post', 'delete'], url_path='subscribe',
            serializer_class=SubscriptionSerializer,
            permission_classes=[OwnerAdminOrReadOnly, ])
    def subscribe(self, request, id):
        user = request.user
        follower = get_object_or_404(User, id=id)
        if request.method == 'POST':
            follow = Subscription.objects.create(user=user, follower=follower)
            serializer = self.get_serializer(follow)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        try:
            subscription = Subscription.objects.get(user=user,
                                                    follower=follower)
        except Subscription.DoesNotExist:
            return Response(
                {'error': 'Подписки не существует'},
                status=status.HTTP_400_BAD_REQUEST
            )
        subscription.delete()
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
    permission_classes = (OwnerAdminOrReadOnly,)
    pagination_class = LimitOffsetPagination
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self, *args, **kwargs):
        if self.action in ('list', 'retrieve'):
            return RecipeSerializerGet
        return RecipeSerializerPost

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated, ])
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)
        user = request.user
        if request.method == 'POST':
            favourite, status_create = UserRecipe.objects.get_or_create(
                user=user, recipe=recipe
            )
            if not status_create:
                return Response(
                    {'error': 'Рецепт уже добавлен в избранное'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response(
                {'message': 'Рецепт добавлен в избранное'},
                status=status.HTTP_201_CREATED
            )
        try:
            favourite = UserRecipe.objects.get(user=user, recipe=recipe)
        except UserRecipe.DoesNotExist:
            return Response(
                {'error': 'Рецепт не добавлен в избранное'},
                status=status.HTTP_400_BAD_REQUEST
            )
        favourite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticatedOrReadOnly, ])
    def shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)
        user = request.user
        if request.method == 'POST':
            cart, status_create = ShoppingCart.objects.get_or_create(
                user=user,
                recipe=recipe
            )
            if not status_create:
                return Response(
                    {'error': 'Рецепт уже добавлен в список покупок'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response(
                {'message': 'Рецепт добавлен в список покупок'},
                status=status.HTTP_201_CREATED
            )
        try:
            cart = ShoppingCart.objects.get(user=user, recipe=recipe)
        except ShoppingCart.DoesNotExist:
            return Response(
                {'error': 'Нельзя удалить рецепт из списка покупок'},
                status=status.HTTP_400_BAD_REQUEST
            )
        cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], url_path='download_shopping_cart',
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        recipes_in_cart = Recipe.objects.filter(
            shoppingcart__user=request.user
        )
        ingredients = {}
        for recipe in recipes_in_cart:
            for ingredient in recipe.recipeingredient_set.all():
                ingredient_name = (f'{ingredient.ingredient.name}, '
                                   f'{ingredient.ingredient.measurement_unit}')
                ingredients[ingredient_name] = ingredients.setdefault(
                    ingredient_name, 0) + ingredient.amount
        file_content = '\n'.join(
            f'{name}: {amount}' for name, amount in ingredients.items())
        response = FileResponse(file_content, content_type='text/plain')
        response[
            'Content-Disposition'] = 'attachment; filename="shopping_cart.txt"'
        return response

    @action(detail=True, methods=['get'], url_path='get-link',
            permission_classes=(AllowAny,))
    def get_link(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)
        url = f'{request.get_host()}/s/' + recipe.short_url
        return Response({'short-link': url}, status=status.HTTP_200_OK)
