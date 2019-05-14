import logging
from django.apps import AppConfig

logger = logging.getLogger(__name__)


class FaxConfig(AppConfig):
    name = "fax"

    def ready(self):
        from fax import tasks
        logger.warning(f'Fax Module Ready: loaded tasks - {id(tasks)}')
