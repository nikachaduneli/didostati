from django.db import models
from django.utils.translation import gettext_lazy as _
from django_ckeditor_5.fields import CKEditor5Field

from core.models import SluggedModel, Translatable


class Page(Translatable, models.Model):
    """Editable static page (About us, Contact...). The slug is chosen by hand: the menu links to it."""
    slug = models.SlugField(_('slug'), unique=True, help_text=_('"about" and "contact" are used by the menu.'))
    title = models.CharField(_('title'), max_length=200)
    title_ka = models.CharField(_('title (Georgian)'), max_length=200, blank=True)
    content = CKEditor5Field(_('content'), blank=True, config_name='default')
    content_ka = CKEditor5Field(_('content (Georgian)'), blank=True, config_name='default')
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('page')
        verbose_name_plural = _('pages')

    def __str__(self):
        return self.title


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
