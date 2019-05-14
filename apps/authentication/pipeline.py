import logging
import json

from django.contrib.auth import get_user_model

from lazy_clients import LazyLoadedAuth0Client as Auth0Client
from authentication.models import Token

from social_core.exceptions import AuthFailed

logger = logging.getLogger(__name__)
USER_FIELDS = ["given_name", "family_name", "email", "phone_number"]


def get_or_create_user(strategy, details, backend, user=None, *args, **kwargs):
    if backend.name != "auth0":
        return

    User = get_user_model()

    if user:
        return {"is_new": False}

    fields = dict(
        (name, kwargs.get(name, details.get(name)))
        for name in backend.setting("USER_FIELDS", USER_FIELDS)
    )
    if not fields:
        return

    uid = details.get("user_id")
    user_queryset = User.objects.filter(auth0_user_id=uid)
    if user_queryset.exists():
        user = user_queryset.first()
        logger.warning(f"fetched user:{user.uuid} by auth0:user_id")
        return {"is_new": False, "user": user}

    email = details.get("email", "").strip().lower()

    if not email:
        client = Auth0Client().get_client()
        user = client.users.get(uid)
        email = user.get("email")

    user_queryset = User.objects.filter(email=email)
    if user_queryset.exists():
        user = user_queryset.first()
        logger.warning(f"fetched user:{user.uuid} by email")
        return {"is_new": False, "user": user}

    raise AuthFailed(backend, 'User is not registered.')

def cycle_user_auth_token(strategy, user, *args, **kwargs):
    if not user:
        return
    logger.warning(f"cycling token for user:{user.uuid}")
    token, created = Token.objects.get_or_create(user=user)
    token.cycle(strategy.request)
