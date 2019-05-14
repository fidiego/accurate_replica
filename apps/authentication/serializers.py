from rest_framework import serializers

from django.contrib.auth import get_user_model


class LiteUserModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = (
            'uuid',
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'image_url',
        )

        read_only_fields = (
            'uuid',
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'image_url',
        )


class UserModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = (
            'uuid',
            'first_name',
            'last_name',
            'email',
            'email_verified_on',
            'phone_number',
            'phone_number_verified_on',
            'image_url',
            'date_joined',
            'last_login',
            'is_active',
            'is_staff',
            'is_superuser',
        )

        read_only_fields = (
            'uuid',
            'email_verified_on',
            'phone_number_verified_on',
            'date_joined',
            'last_login',
            'is_active',
            'is_staff',
            'is_superuser',
        )

    def clean_email(self, value):
        return value.strip().lower()

    def clean_phone_number(self, value):
        # TODO: assumes US-based phone number
        value = ''.join([c for c in value.strip() if c.isidigit()])
        if len(value) == 10:
            return f'+1{value}'
        if len(value) == 11 and value[0] == 1:
            return f'+{value}'

    def update(self, instance, validated_data):
        email = validated_data.get('email', None)
        if email and email != instance.email:
            instance.email_verified_on = None
            instance.save()

        phone_number = validated_data.get('phone_number', None)
        if phone_number and phone_number != instance.phone_number:
            instance.phone_number_verified_on = None
            instance.save()

        return super().update(instance, validated_data)
