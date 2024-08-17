from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Download ingredients from csv file'

    def handle(self, *args, **options):
        print('Начинаю загрузку ингредиентов в базу...')
        with open('../data/ingredients.csv', 'r', encoding='utf-8') as file:
            from recipes.models import Ingredient
            for ingredient in file.read().rstrip().split('\n'):
                index = ingredient.rindex(',')
                name, measurement_unit = (
                    ingredient[:index],
                    ingredient[index + 1:]
                )
                try:
                    Ingredient.objects.get_or_create(
                        name=name,
                        measurement_unit=measurement_unit
                    )
                except ValueError as error:
                    print(error, ingredient)
        print(
            f'Загрузка ингредиентов в базу - ЗАВЕРШЕНА!\n'
            f'Всего ингредиентов в базе: {Ingredient.objects.count()}\n'
            f'-----------------------------------------------'
        )

        from recipes.models import Tag
        print('Начинаю загрузку тегов в базу...')
        tags = [
            ('tag1', 'tag1'),
            ('tag2', 'tag2'),
            ('tag3', 'tag3'),
        ]
        for tag in tags:
            try:
                Tag.objects.get_or_create(
                    name=tag[0],
                    slug=tag[1]
                )
            except ValueError as error:
                print(error, tag)
        print(
            f'Загрузка тегов в базу - ЗАВЕРШЕНА!\n'
            f'Всего тегов в базе: {Tag.objects.count()}\n'
            f'-----------------------------------------------\n'
        )
