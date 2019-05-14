import logging
import urllib.parse

from django.conf import settings
from django.http import HttpResponse
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from fax.models import Fax
from fax.tasks import _receive_fax

logger = logging.getLogger(__name__)


class GetRequestBody:
    def get_request_body(self, request):
        """returns query params as a dictionary
        used for storing call query params in metadata json field"""
        query_params = request.body.decode().split("&")
        return {
            k.strip(): urllib.parse.unquote(v.strip())
            for k, v in [t.split("=") for t in query_params]
        }


class FaxStatusCallback(View, GetRequestBody):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, uuid):
        body = self.get_request_body(request)
        logger.warning(body)

        queryset = Fax.objects.filter(uuid=uuid)
        if not queryset.exists():
            return HttpResponse("", content_type="text/plain", status=404)

        fax = queryset.first()
        fax.status = body["Status"]
        fax.fax_status = body["FaxStatus"]
        if body.get("ErrorMessage"):
            fax.error_message = body["ErrorMessage"]
        fax.save()

        return HttpResponse("", content_type="text/plain", status=200)


class FaxSentView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request):
        action = f'{settings.URL}{reverse("fax:received")}'
        response = f'<Response><Receive action="{action}" /></Response>'
        return HttpResponse(response, content_type="text/xml", status=200)


class FaxReceivedView(View, GetRequestBody):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request):
        body = self.get_request_body(request)
        fax = Fax.objects.create(
            status=body['Status'],
            sid=body['FaxSid'],
            fax_status=body['FaxStatus'],
            _from=body['From'],
            _to=body['To'],
            direction='inbound',
            twilio_metadata=[body],
        )
        _receive_fax.delay(fax.uuid)
        return HttpResponse("", content_type="text/plain", status=200)
