from rest_framework import serializers


class ImageField(serializers.ImageField):
    """Return site-relative URLs so they work behind any proxy/host."""

    def to_representation(self, value):
        return value.url if value else None


class TranslatedMixin:
    """Swaps the fields listed in `Meta.translated` for their Georgian value when that language is active."""

    def to_representation(self, instance):
        data = super().to_representation(instance)
        for field in getattr(self.Meta, 'translated', ()):
            data[field] = instance.tr(field)
        return data
