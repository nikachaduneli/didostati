from rest_framework import serializers

from core.serializers import ImageField, TranslatedMixin
from . import models


class PageSerializer(TranslatedMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Page
        fields = ('slug', 'title', 'content')
        translated = ('title', 'content')


class BlogListSerializer(TranslatedMixin, serializers.ModelSerializer):
    cover_image = ImageField()

    class Meta:
        model = models.Blog
        fields = ('id', 'title', 'slug', 'cover_image', 'excerpt', 'created_at')
        translated = ('title', 'excerpt')


class BlogDetailSerializer(BlogListSerializer):
    class Meta(BlogListSerializer.Meta):
        fields = BlogListSerializer.Meta.fields + ('content',)
        translated = ('title', 'excerpt', 'content')


class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ContactMessage
        fields = ('name', 'email', 'message')


class SlideSerializer(TranslatedMixin, serializers.ModelSerializer):
    image = ImageField()

    class Meta:
        model = models.Slide
        fields = ('id', 'image', 'title', 'subtitle', 'link')
        translated = ('title', 'subtitle')
