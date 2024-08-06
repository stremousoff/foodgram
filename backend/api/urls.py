from django.urls import path, include
from djoser.views import UserViewSet
from rest_framework.routers import DefaultRouter

from .views import AvatarView, TagViewSet, IngredientViewSet, RecipeViewSet

router = DefaultRouter()

router.register('tags', viewset=TagViewSet, basename='tags')
router.register('ingredients', viewset=IngredientViewSet, basename='ingredients')
router.register('recipes', viewset=RecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('users/me/avatar/', AvatarView.as_view()),
    path('users/', UserViewSet.as_view({'get': 'list'})),
]
