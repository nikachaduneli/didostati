from decimal import Decimal

from django.conf import settings
from django.core.validators import MaxValueValidator
from django.db import models
from django.utils.text import slugify
from django.utils.translation import get_language, gettext_lazy as _
from django_ckeditor_5.fields import CKEditor5Field


class Translatable:
    """`tr('name')` returns `name_ka` when the active language is Georgian and it is filled in."""

    def tr(self, field):
        if (get_language() or '').startswith('ka'):
            value = getattr(self, f'{field}_ka', '')
            if value:
                return value
        return getattr(self, field)


class SluggedModel(Translatable, models.Model):
    """Fills `slug` from `name`/`title` when left empty, keeping it unique."""
    slug_source = 'name'

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(getattr(self, self.slug_source)) or 'item'
            slug, n = base, 2
            while type(self).objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug, n = f'{base}-{n}', n + 1
            self.slug = slug
        super().save(*args, **kwargs)


class Category(SluggedModel):
    name = models.CharField(_('name'), max_length=120)
    name_ka = models.CharField(_('name (Georgian)'), max_length=120, blank=True)
    slug = models.SlugField(_('slug'), unique=True, blank=True)
    image = models.ImageField(_('image'), upload_to='categories/')
    description = models.TextField(_('description'), blank=True)
    description_ka = models.TextField(_('description (Georgian)'), blank=True)
    order = models.PositiveIntegerField(_('position'), default=0, help_text=_('Lower numbers appear first.'))

    class Meta:
        ordering = ['order', 'name']
        verbose_name = _('category')
        verbose_name_plural = _('categories')

    def __str__(self):
        return self.name


class Color(Translatable, models.Model):
    name = models.CharField(_('name'), max_length=60, unique=True)
    name_ka = models.CharField(_('name (Georgian)'), max_length=60, blank=True)
    hex = models.CharField(_('hex code'), max_length=7, default='#000000', help_text=_('e.g. #ff0000'))

    class Meta:
        ordering = ['name']
        verbose_name = _('colour')
        verbose_name_plural = _('colours')

    def __str__(self):
        return self.name


class Product(SluggedModel):
    category = models.ForeignKey(Category, verbose_name=_('category'), on_delete=models.CASCADE,
                                 related_name='products')
    name = models.CharField(_('name'), max_length=200)
    name_ka = models.CharField(_('name (Georgian)'), max_length=200, blank=True)
    slug = models.SlugField(_('slug'), unique=True, blank=True)
    description = models.TextField(_('description'), blank=True)
    description_ka = models.TextField(_('description (Georgian)'), blank=True)
    price = models.DecimalField(_('price'), max_digits=10, decimal_places=2)
    discount_percent = models.PositiveSmallIntegerField(
        _('discount percent'), default=0, validators=[MaxValueValidator(100)],
        help_text=_('0 = no discount. E.g. 20 takes 20% off the price.'))
    colors = models.ManyToManyField(Color, verbose_name=_('colours'), blank=True, related_name='products')
    is_popular = models.BooleanField(_('popular'), default=False,
                                     help_text=_('Show in "Popular products" on the main page.'))
    is_active = models.BooleanField(_('active'), default=True, help_text=_('Untick to hide from the shop.'))
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('product')
        verbose_name_plural = _('products')

    def __str__(self):
        return self.name

    @property
    def final_price(self):
        if not self.discount_percent:
            return self.price
        return (self.price * (100 - self.discount_percent) / Decimal(100)).quantize(Decimal('0.01'))


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(_('image'), upload_to='products/')
    color = models.ForeignKey(Color, verbose_name=_('colour'), null=True, blank=True, on_delete=models.SET_NULL,
                              help_text=_('Optional: show this picture when the customer picks this colour.'))
    order = models.PositiveIntegerField(_('position'), default=0)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = _('product image')
        verbose_name_plural = _('product images')


class Page(Translatable, models.Model):
    """Editable static page (About us, Contact...)."""
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
    slug = models.SlugField(_('slug'), unique=True, blank=True)
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


class Order(AddressFields):
    STATUSES = [('new', _('New')), ('processing', _('Processing')), ('shipped', _('Shipped')),
                ('delivered', _('Delivered')), ('cancelled', _('Cancelled'))]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                             on_delete=models.SET_NULL, related_name='orders')
    email = models.EmailField(_('email'))
    note = models.TextField(_('note'), blank=True)
    status = models.CharField(_('status'), max_length=20, choices=STATUSES, default='new')
    total = models.DecimalField(_('total'), max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('order')
        verbose_name_plural = _('orders')

    def __str__(self):
        return f'Order #{self.pk}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, null=True, on_delete=models.SET_NULL)
    product_name = models.CharField(_('product name'), max_length=200)
    color_name = models.CharField(_('colour'), max_length=60, blank=True)
    unit_price = models.DecimalField(_('unit price'), max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(_('quantity'), default=1)

    class Meta:
        verbose_name = _('order item')
        verbose_name_plural = _('order items')

    @property
    def line_total(self):
        return self.unit_price * self.quantity
