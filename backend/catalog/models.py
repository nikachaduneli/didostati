from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_ckeditor_5.fields import CKEditor5Field

from core.models import SluggedModel, Translatable


class Category(SluggedModel):
    name = models.CharField(_('name'), max_length=120)
    name_ka = models.CharField(_('name (Georgian)'), max_length=120, blank=True)
    image = models.ImageField(_('image'), upload_to='categories/')
    description = CKEditor5Field(_('description'), blank=True, config_name='default')
    description_ka = CKEditor5Field(_('description (Georgian)'), blank=True, config_name='default')
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
    description = CKEditor5Field(_('description'), blank=True, config_name='default')
    description_ka = CKEditor5Field(_('description (Georgian)'), blank=True, config_name='default')
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
    def is_collection(self):
        return self.bundle_items.exists()

    def discounted(self, price):
        if not self.discount_percent:
            return price
        return (price * (100 - self.discount_percent) / Decimal(100)).quantize(Decimal('0.01'))

    @property
    def final_price(self):
        return self.discounted(self.price)


class ProductSize(Translatable, models.Model):
    product = models.ForeignKey(Product, verbose_name=_('product'), on_delete=models.CASCADE, related_name='sizes')
    name = models.CharField(_('name'), max_length=60, help_text=_('e.g. S, M, L or 30x40 cm'))
    name_ka = models.CharField(_('name (Georgian)'), max_length=60, blank=True)
    price = models.DecimalField(_('price'), max_digits=10, decimal_places=2, null=True, blank=True,
                                help_text=_("Leave empty to use the product's price."))
    order = models.PositiveIntegerField(_('position'), default=0)

    class Meta:
        ordering = ['order', 'id']
        unique_together = ('product', 'name')
        verbose_name = _('size')
        verbose_name_plural = _('sizes')

    def __str__(self):
        return self.name

    @property
    def effective_price(self):
        return self.product.price if self.price is None else self.price

    @property
    def final_price(self):
        return self.product.discounted(self.effective_price)


class CollectionItem(models.Model):
    """A product that is part of a collection. A collection is an ordinary Product (own price, images,
    stock-free cart/order flow) that simply has items listed here."""
    collection = models.ForeignKey(Product, verbose_name=_('collection'), on_delete=models.CASCADE,
                                   related_name='bundle_items')
    product = models.ForeignKey(Product, verbose_name=_('product'), on_delete=models.CASCADE,
                                related_name='in_collections')
    quantity = models.PositiveSmallIntegerField(_('quantity'), default=1)

    class Meta:
        unique_together = ('collection', 'product')
        verbose_name = _('collection item')
        verbose_name_plural = _('collection items')

    def __str__(self):
        return f'{self.quantity} × {self.product}'

    def clean(self):
        if self.product_id and self.collection_id:
            if self.product_id == self.collection_id:
                raise ValidationError(_('A collection cannot contain itself.'))
            if self.product.bundle_items.exists():
                raise ValidationError(_('A collection cannot contain another collection.'))
            if self.collection.in_collections.exists():
                raise ValidationError(_('This product is already part of a collection.'))


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

    def __str__(self):
        return f'{self.product} #{self.order}'
