import logging

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


logger = logging.getLogger(__name__)


class AuthenticationConfig(AppConfig):
    name = "authentication"
    verbose_name = _("Authentication")

    def ready(self):
        from authentication import signals
        from authentication import tasks

        logger.warning(
            f"Authentication Ready: loaded signals and tasks - {id(signals)}:{id(tasks)}"
        )
