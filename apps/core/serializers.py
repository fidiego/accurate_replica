from django.contrib.auth import get_user_model

from rest_framework import serializers


class UserModelSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    token = serializers.SerializerMethodField()
    organizations = serializers.SerializerMethodField()
    twilio_worker_sid = serializers.SerializerMethodField()
    groups = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = (
            "uuid",
            "email",
            "full_name",
            "groups",
            "organizations",
            "phone_number",
            "token",
            "twilio_worker_sid",
            "image_url",
            "is_superuser",
            "is_staff",
        )
        read_only_fields = fields

    def get_full_name(self, user):
        return user.get_full_name()

    def get_token(self, user):
        return user.auth_token.key

    def get_organizations(self, user):
        return [org.short_name for org in user.organizations.all()]

    def get_twilio_worker_sid(self, user):
        if hasattr(user, "agent") and user.agent:
            return user.agent.twilio_worker_sid

    def get_groups(self, user):
        groups = [g.name for g in user.groups.all()]
        if user.is_superuser:
            groups += ['supervisor', 'wfo.full_access']
        return groups
