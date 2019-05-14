import logging

from django.conf import settings
from django import forms

from core.formatters import e164_format_phone_number
from fax.models import Fax
from fax.tasks import _send_fax


class OutboundFaxForm(forms.Form):
    to = forms.CharField(max_length=17, label="to")
    content = forms.FileField()

    def __init__(self, *args, **kwargs):
        self.created_by = kwargs.pop('created_by', None)
        super(OutboundFaxForm, self).__init__(*args, **kwargs)

    def clean_to(self):
        to = self.cleaned_data.get('to', '').strip()
        if not to:
            raise forms.ValidationError('Please provide a valid fax number.')
        cleaned = e164_format_phone_number(to)
        return cleaned

    def clean_content(self):
        content = self.cleaned_data['content']
        return content

    def clean(self):
        super().clean()
        logging.warning(self.cleaned_data)

        to = self.cleaned_data['to']
        if to == settings.TWILIO_NUMBER:
            raise forms.ValidationError('Sending fax to self is disallowed.')
        return self.cleaned_data

    def save(self):
        kwargs = self.cleaned_data
        kwargs['_to'] = kwargs.pop('to')  # N.B. update to match the model field
        fax = Fax.objects.create(created_by=self.created_by, **kwargs)
        _send_fax.delay(fax.uuid)
        return fax
