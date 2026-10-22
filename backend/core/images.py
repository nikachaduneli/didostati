"""Re-encode newly uploaded images to WebP before they are written to storage."""
import os
from io import BytesIO

from django.apps import apps
from django.core.files.base import ContentFile
from django.db import models
from django.db.models.signals import pre_save
from PIL import Image, ImageOps

WEBP_QUALITY = 82


def to_webp(file):
    """Return a ContentFile holding `file` as WebP, or None if it is already WebP."""
    file.seek(0)
    with Image.open(file) as img:
        if img.format == 'WEBP':
            return None
        animated = getattr(img, 'is_animated', False)
        if not animated:
            img = ImageOps.exif_transpose(img)  # bake in camera rotation, EXIF is dropped
        if img.mode not in ('RGB', 'RGBA'):
            has_alpha = img.mode in ('LA', 'PA') or 'transparency' in img.info
            img = img.convert('RGBA' if has_alpha else 'RGB')
        out = BytesIO()
        img.save(out, 'WEBP', quality=WEBP_QUALITY, method=6, save_all=animated)
    stem = os.path.splitext(os.path.basename(file.name))[0]
    return ContentFile(out.getvalue(), name=f'{stem}.webp')


def convert_images(sender, instance, **kwargs):
    for field in sender._meta.get_fields():
        if isinstance(field, models.ImageField):
            file = getattr(instance, field.name)
            # Only fresh uploads; files already in storage are left alone.
            if file and not file._committed:
                webp = to_webp(file)
                if webp is not None:
                    setattr(instance, field.name, webp)


def connect():
    for model in apps.get_models():
        if any(isinstance(f, models.ImageField) for f in model._meta.get_fields()):
            pre_save.connect(convert_images, sender=model, dispatch_uid=f'convert_images_{model._meta.label}')
