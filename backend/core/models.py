from django.db import models
from django.utils.text import slugify
from django.utils.translation import get_language, gettext_lazy as _


class Translatable:
    """`tr('name')` returns `name_ka` when the active language is Georgian and it is filled in."""

    def tr(self, field):
        if (get_language() or '').startswith('ka'):
            value = getattr(self, f'{field}_ka', '')
            if value:
                return value
        return getattr(self, field)


class SluggedModel(Translatable, models.Model):
    """`slug` is computed from `slug_source` (the name/title) on every save and kept unique."""
    slug_source = 'name'

    slug = models.SlugField(_('slug'), unique=True, editable=False, blank=True)

    class Meta:
        abstract = True

    def compute_slug(self):
        base = slugify(getattr(self, self.slug_source)) or 'item'
        slug, n = base, 2
        while type(self).objects.filter(slug=slug).exclude(pk=self.pk).exists():
            slug, n = f'{base}-{n}', n + 1
        return slug

    def save(self, *args, **kwargs):
        self.slug = self.compute_slug()
        update_fields = kwargs.get('update_fields')
        if update_fields is not None:
            kwargs['update_fields'] = {*update_fields, 'slug'}
        super().save(*args, **kwargs)


class AddressFields(models.Model):
    full_name = models.CharField(_('full name'), max_length=120)
    phone = models.CharField(_('phone'), max_length=40)
    line1 = models.CharField(_('address'), max_length=200)
    line2 = models.CharField(_('address 2'), max_length=200, blank=True)
    city = models.CharField(_('city'), max_length=100)
    postal_code = models.CharField(_('postal code'), max_length=20, blank=True)
    country = models.CharField(_('country'), max_length=100)

    class Meta:
        abstract = True
