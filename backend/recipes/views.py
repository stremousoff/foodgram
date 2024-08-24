from django.shortcuts import redirect
from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView

from recipes.models import Recipe


class ShortLinkRedirectView(APIView):
    def get(self, request, short_url):
        recipe = get_object_or_404(Recipe, short_url=short_url)
        return redirect(f'/recipes/{recipe.id}/')
