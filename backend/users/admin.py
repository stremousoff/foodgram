from django.contrib import admin
from django.utils.safestring import mark_safe

from users import models


@admin.register(models.FoodGramUser)
class FoodGramUserAdmin(admin.ModelAdmin):
    list_display = ('image_display', 'username', 'email', 'first_name',
                    'last_name')
    list_filter = ('username',)
    list_display_links = ('image_display', 'username',)
    verbose_name = 'Пользователи'

    @admin.display(description='Аватар')
    def image_display(self, user):
        if user.avatar:
            return mark_safe(
                f'<img src={user.avatar.url} width="60" height="60">'
            )
