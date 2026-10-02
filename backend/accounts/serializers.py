from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from . import models


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Address
        fields = ('id', 'label', 'full_name', 'phone', 'line1', 'line2', 'city',
                  'postal_code', 'country', 'is_default')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ('id', 'email', 'first_name')


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=60, required=False, allow_blank=True)
    password = serializers.CharField(write_only=True)

    def validate_email(self, value):
        value = value.lower()
        if models.User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('An account with this email already exists.')
        return value

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated):
        return models.User.objects.create_user(validated['email'], validated['password'],
                                               first_name=validated.get('first_name', ''))
