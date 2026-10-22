from django.conf import settings
from django.contrib import admin

from . import config, models


@admin.register(models.Config)
class ConfigAdmin(admin.ModelAdmin):
    list_display = ('key', 'shown_value', 'default', 'description')
    search_fields = ('key',)

    @admin.display(description='value')
    def shown_value(self, obj):
        return '••••••' if obj.key in config.SECRET_KEYS and obj.value else obj.value

    @admin.display(description='settings.py default')
    def default(self, obj):
        value = getattr(settings, obj.key)
        return '••••••' if obj.key in config.SECRET_KEYS and value else value
