import os

import django


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodgram.settings')
django.setup()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodgram.settings')
django.setup()


from recipes.models import Recipe, UserRecipe

queryset = UserRecipe.objects.all().filter(user=1)
for q in queryset:
    print(q.recipe)