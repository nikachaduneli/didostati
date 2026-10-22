from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = 'core'

    def ready(self):
        from . import cache, images, signals
        signals.connect()
        images.connect()
        cache.connect()
