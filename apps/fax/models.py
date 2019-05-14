import logging
from tempfile import NamedTemporaryFile

from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.core.files import File
from django.db import models
from django.urls import reverse
import requests

from core.mixins import BaseModelMixin
from core.formatters import pretty_print_phone_number
from lazy_clients import LazyLoadedTwilioClient


logger = logging.getLogger(__name__)


class Fax(BaseModelMixin):
    created_by = models.ForeignKey(
        "authentication.User", on_delete=models.PROTECT, blank=True, null=True
    )

    direction = models.CharField(max_length=16, default="outbound")
    _from = models.CharField(max_length=16, default=settings.DEFAULT_FROM_NUMBER)
    sid = models.CharField(max_length=34, blank=True, null=True)
    status = models.CharField(max_length=16, default="queued")
    fax_status = models.CharField(max_length=16, default="queued")
    error_message = models.CharField(max_length=64, blank=True, null=True)
    _to = models.CharField(max_length=16)
    twilio_metadata = JSONField(default=list, blank=True, null=True)

    content = models.FileField(upload_to="fax-media/")

    # meta fields
    class Meta:
        verbose_name_plural = "faxes"

    def __str__(self):
        return f"{self.direction} Fax: {self.sid}"

    @property
    def logger(self):
        return logging.getLogger(f"FAX:{self.sid}")

    @property
    def resource(self):
        client = LazyLoadedTwilioClient().get_client()
        resource = client.fax.faxes.get(self.sid)
        fax = resource.fetch()
        return fax

    @property
    def short_id(self):
        return str(self.uuid)[-8:]

    @property
    def to_number(self):
        return pretty_print_phone_number(self._to)

    @property
    def from_number(self):
        return pretty_print_phone_number(self._from)

    @property
    def content_url(self):
        if self.content:
            return self.content.url
        return

    def send_fax(self):
        if self.sid:
            self.logger.warning("Fax has already been sent. Nothing to do.")
            # return

        status_callback = f'{settings.URL}{reverse("fax:status-callback", kwargs=dict(uuid=str(self.uuid)))}'
        self.logger.warning(status_callback)
        client = LazyLoadedTwilioClient().get_client()
        fax = client.fax.faxes.create(
            from_=self._from,
            to=self._to,
            media_url=self.content.url,
            status_callback=status_callback,
        )
        self.sid = fax.sid
        self.status = fax.status
        self.save()
        return fax

    def receive_fax(self):
        """
        Invoke in post_create
        """
        if self.direction == "outbound":
            self.logger.info("Fax is outbound. Nothing to do.")
            return

        # 1. take the files from twilio and move them to S3
        resource = self.resource
        media_url = resource.media_url
        req = requests.get(media_url)

        if req.status_code not in [200]:
            self.logger.error("Failed to fetch media url.")
            return

        name = f"{self.uuid}-content.pdf"
        with NamedTemporaryFile() as fp:
            fp.write(req.content)
            fp.seek(0)
            self.content.save(name, File(fp))

        # 2. remove the files from twilio
        return self.content.url
