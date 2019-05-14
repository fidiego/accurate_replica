from rest_framework.viewsets import ModelViewSet

from django.contrib.auth import get_user_model

from authentication.models import User, Token

from authentication.serializers import UserModelSerializer


class UserModelViewSet(ModelViewSet):
    serializer_class = UserModelSerializer

    def get_queryset(self):
        User = get_user_model()
        return User.objects.filter(uuid=self.request.user.uuid)
