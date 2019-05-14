from django.conf import settings
from core.formatters import pretty_print_phone_number


def fax_number(request):
    return {'TWILIO_NUMBER': pretty_print_phone_number(settings.TWILIO_NUMBER)}
