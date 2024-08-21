from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.safestring import mark_safe

from users import models


@admin.register(models.FoodGramUser)
class FoodGramUserAdmin(UserAdmin):
    list_display = ('image_display', 'username', 'email', 'first_name',
                    'last_name', 'count_recipes', 'is_subscribed')
    list_filter = ('username',)
    list_display_links = ('image_display', 'username',)
    list_per_page = 20
    verbose_name = 'Пользователи'

    @admin.display(description='Аватар')
    def image_display(self, user):
        if user.avatar:
            return mark_safe(
                f'<img src={user.avatar.url} width="60" height="60">'
            )

    @staticmethod
    def count_recipes(user):
        return user.recipes.count()

    @staticmethod
    def is_subscribed(user):
        return user.followers.count()
