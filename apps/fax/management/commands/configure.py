from django.core.management.base import BaseCommand, CommandError

from lazy_clients import LazyLoadedTwilioClient

from django.conf import settings
from django.urls import reverse


class Command(BaseCommand):
    help = 'Configure Twilio Number Endpoints'

    def handle(self, *args, **options):
        self.stdout.write(str(dir(self.style)))
        voice_url = f'{settings.URL}{reverse("fax:sent")}'
        self.stdout.write(self.style.WARNING(f'Configuring Phone Number: {settings.TWILIO_NUMBER_SID}'))
        self.stdout.write(self.style.WARNING(f'               voice url: {voice_url}'))

        client = LazyLoadedTwilioClient().get_client()
        number = client.incoming_phone_numbers.get(settings.TWILIO_NUMBER_SID)
        number.update(voice_url=voice_url)

        self.stdout.write(self.style.SUCCESS('Phone Number Successfully Configured!'))
