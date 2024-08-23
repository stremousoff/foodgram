from django.http import HttpResponse
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from recipes.models import Recipe


def add_object(request, pk, serializer_class):
    recipe_id = get_object_or_404(Recipe, id=pk).id
    user_id = request.user.id
    serializer = serializer_class(
        data={
            'recipe': recipe_id,
            'user': user_id
        }
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


def delete_object(request, pk, model):
    del_object, _ = model.objects.filter(
        user=request.user,
        recipe=pk
    ).delete()
    return Response(
        status=status.HTTP_204_NO_CONTENT
        if del_object
        else status.HTTP_400_BAD_REQUEST
    )


def download_shopping_cart_file(ingredients):
    file_content = '\n'.join(
        f"{ingredient['ingredient__name']}, "
        f"{ingredient['ingredient__measurement_unit']}: "
        f"{ingredient['total_amount']}"
        for ingredient in ingredients
    )
    response = HttpResponse(file_content, content_type='text/plain')
    response[
        'Content-Disposition'] = 'attachment; filename="shopping_cart.txt"'
    return response
