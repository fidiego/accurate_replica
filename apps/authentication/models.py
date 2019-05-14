from datetime import timedelta
from hashlib import sha512
from uuid import uuid4
import binascii
import logging
import os

from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.postgres.fields import JSONField
from django.core import signing
from django.core.mail import send_mail
from django.core.validators import MaxLengthValidator
from django.core.validators import MinLengthValidator
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from authentication.managers import UserManager
from authentication.mixins import Auth0UserModelMixin
from core.mixins import BaseModelMixin
from core.formatters import pretty_print_phone_number


logger = logging.getLogger(__name__)


class User(AbstractBaseUser, PermissionsMixin, Auth0UserModelMixin):
    """
    Custom User Model

    Major Changes Include:
     - uuid as primary key
     - phone number field
     - phone number verification field
     - email verification field

    All else works as expected.
    """

    uuid = models.UUIDField(
        primary_key=True, db_index=True, default=uuid4, editable=False
    )

    date_joined = models.DateTimeField(_("date joined"), auto_now_add=True)
    is_active = models.BooleanField(_("active"), default=True)
    is_staff = models.BooleanField(_("is staff"), default=False)
    is_superuser = models.BooleanField(_("is superuser"), default=False)

    first_name = models.CharField(_("first name"), max_length=30, blank=True)
    last_name = models.CharField(_("last name"), max_length=30, blank=True)

    email = models.EmailField(
        _("email address"), max_length=128, unique=True, blank=True, null=True
    )
    email_verified_on = models.DateTimeField(
        _("email verified on"), blank=True, null=True
    )

    phone_number = models.CharField(_("phone number"), max_length=16, unique=True)
    phone_number_verified_on = models.DateTimeField(
        _("phone number verified on"), blank=True, null=True
    )

    # image url
    DEFAULT_IMAGE_URL = (
        "https://www.gravatar.com/avatar/85c0bae3b2a1e04908a3c916fbb000f7"
    )
    image_url = models.URLField(default=DEFAULT_IMAGE_URL)
    auth0_user_id = models.CharField(max_length=35, blank=True, null=True)

    # object manager
    objects = UserManager()

    # django user model field enhancments
    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = ["first_name", "last_name", "email"]

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def __str__(self):
        return self.get_full_name() or self.email

    @classmethod
    def load_set_password_token(cls, signed):
        try:
            value = signing.loads(signed)
            return value
        except signing.BadSignature:
            logger.warning(f"Bad set password token for user:{self.uuid}")
            return

    @property
    def name(self):
        name = self.get_full_name()
        name = " ".join([s.strip() for s in name.split(" ") if s.strip()]).strip()
        return name.strip()

    @property
    def phone_number__prettified(self):
        return pretty_print_phone_number(self.phone_number)

    @property
    def phone_number_verified(self):
        return self.phone_number and self.phone_number_verified_on is not None

    @property
    def email_verified(self):
        return self.email and self.email_verified_on is not None

    @property
    def has_password(self):
        return self.password not in [None, ""]

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        """
        Returns the short name for the user.
        """
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def verify_phone_number(self):
        self.phone_number_verified_on = timezone.now()
        self.save()

    def gen_set_password_token(self):
        # TODO: consider making the timedelta a setting
        expires = timezone.now() + timedelta(hours=4)
        value = f"{self.phone_number}::{int(expires.timestamp())}"
        signed = signing.dumps(value)
        return signed

    def is_hotline_admin(self):
        return self.groups.filter(name="hotline_admin").exists()


class Token(BaseModelMixin):
    key = models.CharField(_("Key"), max_length=40, db_index=True)

    user_agent = models.CharField(max_length=256, blank=True, null=True)

    # sha512 hashed ip addres
    ip_address_hash = models.CharField(
        max_length=128,
        validators=[
            MinLengthValidator(128),
            MaxLengthValidator(128),
            RegexValidator(r"[0-9a-f]{128}"),  # https://regex101.com/r/B9agTJ/1
        ],
        blank=True,
        null=True,
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name="auth_token",
        on_delete=models.CASCADE,
        verbose_name=_("User"),
    )

    class Meta:
        # Work around for a bug in Django:
        # https://code.djangoproject.com/ticket/19422
        #
        # Also see corresponding ticket:
        # https://github.com/encode/django-rest-framework/issues/705
        abstract = "authentication" not in settings.INSTALLED_APPS
        verbose_name = _("Token")
        verbose_name_plural = _("Tokens")

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super(Token, self).save(*args, **kwargs)

    def regenerate_key(self):
        self.key = self.generate_key()

    def generate_key(self):
        return binascii.hexlify(os.urandom(20)).decode()

    def __str__(self):
        return self.key

    def token(self):
        return f'{self.key[:2]}{"*" * 36}{self.key[-2:]}'

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip

    def get_user_agent(self, request):
        return request.META.get("HTTP_USER_AGENT")

    def cycle(self, request):
        # regenerate key
        self.regenerate_key()

        # add hashed ip address
        ip_address = self.get_client_ip(request)
        ip_address_hash = sha512(ip_address.encode("utf-8")).hexdigest()
        self.ip_address_hash = ip_address_hash

        # add user agent
        self.user_agent = self.get_user_agent(request)
        self.save()
        logger.warning(f"updated token for user:{self.user.uuid}")
