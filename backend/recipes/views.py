from django.shortcuts import redirect
from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView

from recipes.models import Recipe


class ShortLinkRedirectView(APIView):
    def get(self, request, slug):
        recipe = get_object_or_404(Recipe, short_url=slug)
        return redirect(f'/recipes/{recipe.id}/')
