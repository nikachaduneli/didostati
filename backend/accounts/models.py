from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import AddressFields
from .managers import UserManager


class User(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return self.email


class Address(AddressFields):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='addresses')
    label = models.CharField(_('label'), max_length=60, blank=True, help_text=_('e.g. Home, Work'))
    is_default = models.BooleanField(_('default'), default=False)

    class Meta:
        ordering = ['-is_default', '-id']
        verbose_name = _('address')
        verbose_name_plural = _('addresses')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.is_default:
            Address.objects.filter(user=self.user).exclude(pk=self.pk).update(is_default=False)

    def __str__(self):
        return f'{self.label or "Address"} – {self.full_name}'
