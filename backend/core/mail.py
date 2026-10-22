"""Email backend for MAILERS that reads the SMTP settings through core.config on every send,
so SMTP details changed in the admin apply without a restart."""
from django.core.mail.backends.console import EmailBackend as ConsoleBackend
from django.core.mail.backends.smtp import EmailBackend as SMTPBackend

from . import config


def mailer(alias, **options):
    """Until SMTP_HOST is filled in, messages are printed to the console."""
    host = config.get('SMTP_HOST')
    if not host:
        return ConsoleBackend(alias=alias, **options)
    return SMTPBackend(
        alias=alias, host=host, port=config.get('SMTP_PORT'), username=config.get('SMTP_USER'),
        password=config.get('SMTP_PASSWORD'), use_tls=config.get('SMTP_USE_TLS'), **options,
    )
