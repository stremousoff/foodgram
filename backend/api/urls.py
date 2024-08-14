from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (IngredientViewSet, RecipeViewSet, TagViewSet,
                    UserFoodgramViewSet)

router = DefaultRouter()

router.register('tags', viewset=TagViewSet, basename='tags')
router.register('ingredients', viewset=IngredientViewSet,
                basename='ingredients')
router.register('recipes', viewset=RecipeViewSet, basename='recipes')
router.register('users', viewset=UserFoodgramViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
