"""Cache public API responses in Redis.

Every key includes a version number; any change to a catalog or content row bumps it,
so admin edits show up immediately instead of after the timeout.
"""
import time

from django.apps import apps
from django.core.cache import cache
from django.db.models.signals import m2m_changed, post_delete, post_save
from django.utils import translation
from rest_framework.response import Response

VERSION_KEY = 'api:version'
TIMEOUT = 15 * 60
CACHED_APPS = ('catalog', 'content')


def bump_version(**kwargs):
    cache.set(VERSION_KEY, time.time_ns(), None)


class CachedResponseMixin:
    """For read-only views: GET responses are served from the cache."""

    def _cached(self, request, view, *args, **kwargs):
        key = f'api:{cache.get(VERSION_KEY, 0)}:{translation.get_language()}:{request.build_absolute_uri()}'
        data = cache.get(key)
        if data is not None:
            return Response(data)
        response = view(request, *args, **kwargs)
        if response.status_code == 200:
            cache.set(key, response.data, TIMEOUT)
        return response

    def list(self, request, *args, **kwargs):
        return self._cached(request, super().list, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        return self._cached(request, super().retrieve, *args, **kwargs)


def connect():
    for label in CACHED_APPS:
        for model in apps.get_app_config(label).get_models():
            uid = f'api_cache_{model._meta.label}'
            post_save.connect(bump_version, sender=model, dispatch_uid=uid)
            post_delete.connect(bump_version, sender=model, dispatch_uid=uid)
            for field in model._meta.many_to_many:
                m2m_changed.connect(bump_version, sender=field.remote_field.through, dispatch_uid=f'{uid}_{field.name}')
