import os

import django


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodgram.settings')
django.setup()


with open('ingredients.csv', 'r', encoding='utf-8') as file:
    from recipes.models import Ingredient
    for ingredient in file.read().rstrip().split('\n'):
        index = ingredient.rindex(',')
        name, measurement_unit = ingredient[:index], ingredient[index + 1:]
        try:
            index = ingredient.rindex(',')
            Ingredient.objects.create(
                name=name,
                measurement_unit=measurement_unit
            ).save()
        except ValueError as error:
            print(error, ingredient)

