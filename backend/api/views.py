from django.contrib.auth import get_user_model
from django.db.models import Count, Sum
from django.http import FileResponse
from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from users.models import Subscription
from .core import add_object, delete_object, shopping_cart_data
from .filters import IngredientFilter, RecipeFilter
from .pagination import PageNumberPaginator
from .permissions import OwnerAdminOrReadOnly
from .serializers import (AvatarSerializer, FavoriteSerializer,
                          FoodGramUserSerializer, IngredientSerializer,
                          GetRecipeSerializer, UpdateCreateRecipeSerializer,
                          ShoppingCartSerializer, SubscriptionSerializer,
                          SubscriptionsListSerializer, TagSerializer)

User = get_user_model()


class UserFoodgramViewSet(UserViewSet):
    queryset = User.objects.all()
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend,)

    @action(detail=False, url_path='me', permission_classes=(IsAuthenticated,))
    def me(self, request):
        serializer = FoodGramUserSerializer(
            request.user,
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=('put',), url_path='me/avatar',
            permission_classes=(IsAuthenticated,))
    def update_avatar(self, request):
        user = request.user
        serializer = AvatarSerializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @update_avatar.mapping.delete
    def delete_avatar(self, request):
        user = request.user
        if user.avatar:
            user.avatar.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        url_path='subscriptions',
        serializer_class=SubscriptionsListSerializer,
        permission_classes=(OwnerAdminOrReadOnly,)
    )
    def subscriptions(self, request):
        subscriptions = (
            User.objects.filter(subs_from_user__user=request.user)
            .annotate(recipes_count=Count('recipes'))
        )
        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(subscriptions, request)
        serializer = self.get_serializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    @action(detail=True, methods=('post',), url_path='subscribe',
            serializer_class=SubscriptionSerializer,
            permission_classes=(OwnerAdminOrReadOnly,))
    def subscribe(self, request, id):
        serializer = self.get_serializer(
            data={
                'user': request.user.id,
                'author': id
            }
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def unsubscribe(self, request, id):
        deleted_subscription, _ = Subscription.objects.filter(
            user=request.user,
            author=id
        ).delete()
        return Response(
            status=status.HTTP_204_NO_CONTENT
            if deleted_subscription
            else status.HTTP_400_BAD_REQUEST
        )


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
    queryset = (
        Recipe.objects.select_related('author')
        .prefetch_related('tags', 'ingredients')
        .all()
    )
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (OwnerAdminOrReadOnly,)
    pagination_class = PageNumberPaginator
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_serializer_class(self, *args, **kwargs):
        if self.action in ('list', 'retrieve'):
            return GetRecipeSerializer
        return UpdateCreateRecipeSerializer

    @action(detail=True, methods=('post',),
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk=None):
        return add_object(request, pk, FavoriteSerializer)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk=None):
        return delete_object(request, pk, Favorite)

    @action(detail=True, methods=('post',),
            permission_classes=(IsAuthenticatedOrReadOnly,))
    def shopping_cart(self, request, pk=None):
        return add_object(request, pk, ShoppingCartSerializer)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk=None):
        return delete_object(request, pk, ShoppingCart)

    @action(detail=False, methods=('get',), url_path='download_shopping_cart',
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        ingredients = RecipeIngredient.objects.filter(
            recipe__shoppingcart__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(
            total_amount=Sum('amount')
        ).order_by('ingredient__name')
        return FileResponse(
            shopping_cart_data(ingredients),
            content_type='text/plain'
        )

    @action(detail=True, methods=['get'], url_path='get-link',
            permission_classes=(AllowAny,))
    def get_link(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)
        url = request.build_absolute_uri(
            reverse('short_link_redirect', args=[recipe.short_url])
        )
        return Response({'short-link': url}, status=status.HTTP_200_OK)
