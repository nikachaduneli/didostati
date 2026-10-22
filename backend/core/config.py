"""Settings that staff can change in the admin (the Config model) without a redeploy.

`config.get('SMTP_USER')` returns the admin value when it is filled in,
otherwise `settings.SMTP_USER`. The type of the default in settings.py decides how the
stored text is read (bool, int or str).
"""
from django.conf import settings
from django.core.cache import cache
from django.db.models.signals import post_delete, post_migrate, post_save

CACHE_KEY = 'config:values'

# Settings that may be overridden, with the help text shown in the admin. A row for every key is
# created on migrate (see seed); an empty value means "use settings.py". PAYMENT_MOCK_ENABLED is
# left out on purpose: it must never be switchable from the admin of a live shop.
KEYS = {
    'ORDER_NOTIFICATION_EMAIL': 'Address that receives an email for every new order. Empty: no emails.',
    'ORDER_CURRENCY': 'Currency sign used in order emails, e.g. ₾.',
    'DEFAULT_FROM_EMAIL': 'Sender address of outgoing emails. Empty: the SMTP user.',
    'SMTP_HOST': 'Mail server, e.g. smtp.gmail.com.',
    'SMTP_PORT': 'Mail server port, usually 587 (TLS) or 465.',
    'SMTP_USER': 'Login for the mail server, usually the full email address.',
    'SMTP_PASSWORD': 'Password for the mail server (for Gmail an app password).',
    'SMTP_USE_TLS': 'Encrypt the connection to the mail server: true or false.',
    'SITE_URL': 'Public address of the site, e.g. https://didostati.ge. Used for bank return and callback URLs.',
    'BOG_CLIENT_ID': 'Bank of Georgia payments: client ID.',
    'BOG_CLIENT_SECRET': 'Bank of Georgia payments: client secret.',
    'TBC_API_KEY': 'TBC Bank payments: API key.',
    'TBC_CLIENT_ID': 'TBC Bank payments: client ID.',
    'TBC_CLIENT_SECRET': 'TBC Bank payments: client secret.',
    'PAYMENT_CASH_ON_DELIVERY': 'Offer "pay on delivery" at checkout: true or false.',
    'FB_DIDOSTATI': 'Facebook page link shown in the footer.',
    'IG_DIDOSTATI': 'Instagram page link shown in the footer.',
}
# Shown masked in the admin list.
SECRET_KEYS = {'SMTP_PASSWORD', 'BOG_CLIENT_SECRET', 'TBC_API_KEY', 'TBC_CLIENT_SECRET'}
# Bank access tokens (orders/payments.py) were issued for the old credentials.
TOKEN_CACHE_KEYS = ('bog_token', 'tbc_token')


def cast(name, raw):
    """Read the stored text as the type of the settings.py default. Raises ValueError if it does not fit."""
    default = getattr(settings, name)
    if isinstance(default, bool):
        value = raw.strip().lower()
        if value in ('1', 'true', 'yes', 'on'):
            return True
        if value in ('', '0', 'false', 'no', 'off'):
            return False
        raise ValueError('Use true or false.')
    if isinstance(default, int):
        try:
            return int(raw)
        except ValueError:
            raise ValueError('Enter a whole number.') from None
    return raw.strip()


def _values():
    values = cache.get(CACHE_KEY)
    if values is None:
        from .models import Config
        values = dict(Config.objects.values_list('key', 'value'))
        cache.set(CACHE_KEY, values, None)
    return values


def get(name):
    raw = (_values().get(name) or '').strip()
    return cast(name, raw) if raw else getattr(settings, name)


def clear(**kwargs):
    cache.delete_many([CACHE_KEY, *TOKEN_CACHE_KEYS])


def seed(sender, **kwargs):
    """Make sure every key has a row, and keep the descriptions in step with KEYS."""
    from .models import Config
    for key, description in KEYS.items():
        Config.objects.update_or_create(key=key, defaults={'description': description})


def connect():
    from django.apps import apps
    from .models import Config
    post_migrate.connect(seed, sender=apps.get_app_config('core'), dispatch_uid='config_seed')
    post_save.connect(clear, sender=Config, dispatch_uid='config_clear_save')
    post_delete.connect(clear, sender=Config, dispatch_uid='config_clear_delete')
