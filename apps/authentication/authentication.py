"""
Provides various authentication policies.
"""
from __future__ import unicode_literals
from hashlib import sha512
import logging

from django.utils.translation import ugettext_lazy as _

from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication
from rest_framework.authentication import get_authorization_header

from authentication.models import Token


logger = logging.getLogger(__name__)


class TokenAuthentication(BaseAuthentication):
    """
    Simple token based authentication.

    Clients should authenticate by passing the token key in the "Authorization"
    HTTP header, prepended with the string "Token ".  For example:

        Authorization: Token 401f7ac837da42b97f613d789819ff93537bee6a
    """

    keyword = "Token"
    model = Token

    def get_model(self):
        if self.model is not None:
            return self.model
        return Token

    """
    A custom token model may be used, but must have the following properties.

    * key -- The string identifying the token
    * user -- The user to which the token belongs
    """

    def authenticate(self, request):
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None

        if len(auth) == 1:
            msg = _("Invalid token header. No credentials provided.")
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = _("Invalid token header. Token string should not contain spaces.")
            raise exceptions.AuthenticationFailed(msg)

        try:
            token = auth[1].decode()
        except UnicodeError:
            msg = _(
                "Invalid token header. Token string should not contain invalid characters."
            )
            raise exceptions.AuthenticationFailed(msg)

        return self.authenticate_credentials(token, request)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip

    def get_user_agent(self, request):
        return request.META.get("HTTP_USER_AGENT")

    def authenticate_credentials(self, key, request):
        model = self.get_model()
        try:
            token = model.objects.select_related("user").get(key=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed(_("Invalid token."))

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed(_("User inactive or deleted."))

        user_agent_matches = token.user_agent == self.get_user_agent(request)
        if not user_agent_matches:
            logger.warning("Token user-agent mismatch")
            # raise exceptions.AuthenticationFailed(_('Token user-agent mismatch.'))

        client_ip_hash = sha512(self.get_client_ip(request).encode("utf-8")).hexdigest()
        client_ip_matches = token.ip_address_hash == client_ip_hash
        if not client_ip_matches:
            logger.warning("Token client ip mismatch")
            # raise exceptions.AuthenticationFailed(_('Token client ip mismatch.'))

        if not user_agent_matches and not client_ip_matches:
            logger.warning("Token client ip and user-agent mismatch.")
            raise exceptions.AuthenticationFailed(
                _("Token client ip and user-agent mismatch.")
            )

        return (token.user, token)

    def authenticate_header(self, request):
        return self.keyword
