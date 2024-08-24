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

    @admin.display(description='Количество рецептов')
    def count_recipes(self, user):
        return user.recipes.count()

    @admin.display(description='Количество подписок')
    def is_subscribed(self, user):
        return user.subscribers.count()


@admin.register(models.Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
