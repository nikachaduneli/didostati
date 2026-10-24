from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_ckeditor_5.fields import CKEditor5Field

from core.models import SluggedModel, Translatable


class Page(Translatable, models.Model):
    """Editable static page (About us, Contact...), listed in the header menu, optionally under another page."""
    # These two have their own short address (/about, /contact); every other page lives at /page/<slug>.
    SHORT_SLUGS = ('about', 'contact')

    slug = models.SlugField(_('slug'), unique=True, help_text=_('Part of the address: /page/<slug>. "about" and "contact" get /about and /contact.'))
    parent = models.ForeignKey('self', models.CASCADE, null=True, blank=True, related_name='children',
                               verbose_name=_('parent page'), help_text=_('Shows this page in the submenu of the parent.'))
    show_in_menu = models.BooleanField(_('show in menu'), default=True)
    ordering = models.PositiveIntegerField(_('ordering'), default=0)
    title = models.CharField(_('title'), max_length=200)
    title_ka = models.CharField(_('title (Georgian)'), max_length=200, blank=True)
    content = CKEditor5Field(_('content'), blank=True, config_name='default')
    content_ka = CKEditor5Field(_('content (Georgian)'), blank=True, config_name='default')
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        ordering = ['ordering', 'id']
        verbose_name = _('page')
        verbose_name_plural = _('pages')

    def __str__(self):
        return f'{self.parent} › {self.title}' if self.parent_id else self.title

    @property
    def path(self):
        return f'/{self.slug}' if self.slug in self.SHORT_SLUGS else f'/page/{self.slug}'

    def clean(self):
        # The menu has a single level of submenus.
        if self.parent_id and (self.parent_id == self.pk or self.parent.parent_id):
            raise ValidationError({'parent': _('Choose a top-level page.')})
        if self.parent_id and self.pk and self.children.exists():
            raise ValidationError({'parent': _('This page has subpages, so it cannot go under another page.')})


class Blog(SluggedModel):
    slug_source = 'title'
    title = models.CharField(_('title'), max_length=200)
    title_ka = models.CharField(_('title (Georgian)'), max_length=200, blank=True)
    cover_image = models.ImageField(_('cover image'), upload_to='blog/', blank=True)
    excerpt = models.CharField(_('excerpt'), max_length=300, blank=True, help_text=_('Short teaser shown on cards.'))
    excerpt_ka = models.CharField(_('excerpt (Georgian)'), max_length=300, blank=True)
    content = CKEditor5Field(_('content'), blank=True, config_name='default')
    content_ka = CKEditor5Field(_('content (Georgian)'), blank=True, config_name='default')
    is_published = models.BooleanField(_('published'), default=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('blog post')
        verbose_name_plural = _('blog posts')

    def __str__(self):
        return self.title


class ContactMessage(models.Model):
    name = models.CharField(_('name'), max_length=120)
    email = models.EmailField(_('email'))
    message = models.TextField(_('message'))
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('contact message')
        verbose_name_plural = _('contact messages')

    def __str__(self):
        return f'{self.name} <{self.email}>'


class Slide(Translatable, models.Model):
    """Big banner image in the home page slider."""
    image = models.ImageField(_('image'), upload_to='slides/', help_text=_('Wide image, e.g. 1920x700.'))
    title = models.CharField(_('title'), max_length=200, blank=True)
    title_ka = models.CharField(_('title (Georgian)'), max_length=200, blank=True)
    subtitle = models.CharField(_('subtitle'), max_length=300, blank=True)
    subtitle_ka = models.CharField(_('subtitle (Georgian)'), max_length=300, blank=True)
    link = models.CharField(_('link'), max_length=300, blank=True, help_text=_('Optional, e.g. /shop or https://...'))
    order = models.PositiveIntegerField(_('order'), default=0)
    is_active = models.BooleanField(_('active'), default=True)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = _('slide')
        verbose_name_plural = _('slides')

    def __str__(self):
        return self.title or f'Slide {self.pk}'


class Partner(Translatable, models.Model):
    """Partner logo shown at the bottom of every page."""
    name = models.CharField(_('name'), max_length=120)
    name_ka = models.CharField(_('name (Georgian)'), max_length=120, blank=True)
    logo = models.ImageField(_('logo'), upload_to='partners/')
    link = models.URLField(_('link'), blank=True, help_text=_('Optional website address, e.g. https://example.com'))
    order = models.PositiveIntegerField(_('order'), default=0)
    is_active = models.BooleanField(_('active'), default=True)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = _('partner')
        verbose_name_plural = _('partners')

    def __str__(self):
        return self.name
