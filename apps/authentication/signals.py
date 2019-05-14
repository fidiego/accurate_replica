import logging

from django.dispatch import receiver
from django.db.models.signals import post_save
from django.conf import settings

from authentication.models import Token


logger = logging.getLogger(__name__)
