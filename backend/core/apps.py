from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = 'core'

    def ready(self):
        from . import cache, config, images, signals
        signals.connect()
        images.connect()
        cache.connect()
        config.connect()
