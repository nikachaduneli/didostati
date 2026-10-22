"""Login (bearer) tokens kept in Redis instead of the database.

`auth:token:<key>` holds the user id and expires AUTH_TOKEN_TTL seconds after the token was last used.
"""
import secrets
from functools import cache

import redis
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication


@cache
def _redis():
    return redis.Redis.from_url(settings.REDIS_TOKENS_URL, decode_responses=True)


def create(user):
    key = secrets.token_hex(20)
    _redis().set(f'auth:token:{key}', user.pk, ex=settings.AUTH_TOKEN_TTL)
    return key


def revoke(key):
    _redis().delete(f'auth:token:{key}')


class RedisTokenAuthentication(TokenAuthentication):
    """Accepts `Authorization: Bearer <key>`."""
    keyword = 'Bearer'

    def authenticate_credentials(self, key):
        user_id = _redis().getex(f'auth:token:{key}', ex=settings.AUTH_TOKEN_TTL)
        user = get_user_model().objects.filter(pk=user_id, is_active=True).first() if user_id else None
        if not user:
            raise exceptions.AuthenticationFailed('Invalid token.')
        return user, key
