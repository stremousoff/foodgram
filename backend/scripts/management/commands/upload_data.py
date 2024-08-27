from django.core.management.base import BaseCommand

from recipes.models import Ingredient, Tag


class Command(BaseCommand):
    help = 'Download ingredients and tags from csv file'

    def handle(self, *args, **options):
        self.stdout.write(
            f'Начинаю загрузку {Ingredient._meta.verbose_name} в базу...'
        )
        with open('ingredients.csv', 'r', encoding='utf-8') as file:
            ingredients = [
                Ingredient(name=name, measurement_unit=measurement_unit)
                for line in file
                for name, measurement_unit in [line.strip().rsplit(',', 1)]
            ]
            Ingredient.objects.bulk_create(ingredients, ignore_conflicts=True)
        self.stdout.write(
            f'Загрузка {Ingredient._meta.verbose_name} в базу - ЗАВЕРШЕНА\n'
            f'Всего ингредиентов в базе: {Ingredient.objects.count()}\n'
            f'-----------------------------------------------'
        )
        tags = [
            ('завтрак', 'breakfast'),
            ('обед', 'lunch'),
            ('ужин', 'dinner'),
        ]
        self.stdout.write(
            f'Начинаю загрузку {Tag._meta.verbose_name} тегов в базу...'
        )
        tag_objects = [
            Tag(name=name, slug=slug) for name, slug in tags
        ]
        Tag.objects.bulk_create(tag_objects, ignore_conflicts=True)
        self.stdout.write(
            f'Загрузка {Tag._meta.verbose_name} в базу - ЗАВЕРШЕНА\n'
            f'Всего тегов в базе: {Tag.objects.count()}\n'
            f'-----------------------------------------------'
        )
