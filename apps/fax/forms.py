from django.conf import settings
from django import forms

from core.formatters import e164_format_phone_number
from fax.models import Fax
from fax.tasks import _send_fax


class OutboundFaxForm(forms.ModelForm):
    class Meta:
        model = Fax
        fields = ["_to", "content"]

    def __init__(self, *args, **kwargs):
        self.created_by = kwargs.pop('created_by', None)
        super(OutboundFaxForm, self).__init__(*args, **kwargs)

    def clean__to(self):
        _to = self.cleaned_data['_to']
        cleaned = e164_format_phone_number(_to)
        return cleaned

    def clean_content(self):
        content = self.cleaned_data['content']
        return content

    def clean(self):
        super().clean()

        _to = self.cleaned_data['_to']
        if _to == settings.TWILIO_NUMBER:
            raise forms.ValidationError('Sending fax to self is disallowed.')
        return self.cleaned_data

    def save(self):
        kwargs = self.cleaned_data
        fax = Fax.objects.create(created_by=self.created_by, **kwargs)
        _send_fax.delay(fax.uuid)
        return fax
