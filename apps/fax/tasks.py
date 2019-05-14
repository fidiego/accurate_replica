import logging

from celery import shared_task

from fax.models import Fax


@shared_task
def _receive_fax(uuid):
    fax = Fax.objects.get(uuid=uuid)
    fax.receive_fax()


@shared_task
def _send_fax(uuid):
    fax = Fax.objects.get(uuid=uuid)
    fax.send_fax()
