"""Remove uploaded files from storage when the row that owns them is deleted."""
from django.apps import apps
from django.db import models, transaction
from django.db.models.signals import post_delete


def delete_files(sender, instance, **kwargs):
    for field in sender._meta.get_fields():
        if isinstance(field, models.FileField):  # ImageField is a FileField
            file = getattr(instance, field.name)
            if file and file.name:
                # Only after the delete is committed, so a rollback never loses files.
                transaction.on_commit(lambda f=file: f.storage.delete(f.name))


def connect():
    for model in apps.get_models():
        if any(isinstance(f, models.FileField) for f in model._meta.get_fields()):
            post_delete.connect(delete_files, sender=model, dispatch_uid=f'delete_files_{model._meta.label}')
