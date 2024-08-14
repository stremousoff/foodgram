from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from recipes.models import Recipe


class ShortLinkRedirectView(APIView):
    def get(self, request, short_url):
        try:
            recipe = Recipe.objects.get(short_url=short_url)
            return redirect(f'/api/recipes/{recipe.id}/')
        except Recipe.DoesNotExist:
            return Response(
                {'error': 'Recipe not found'},
                status=status.HTTP_404_NOT_FOUND
            )


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('s/<str:short_url>/', ShortLinkRedirectView.as_view(),
         name='short_link_redirect'),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
