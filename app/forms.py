from django import forms
from django.utils import timezone
from django.forms import ModelForm
from .models import Sample

class DateTimeInput(forms.DateTimeInput):
    input_type = "datetime-local"

    def __init__(self, **kwargs):
        kwargs["format"] = "%Y-%m-%dT%H:%M"
        super().__init__(**kwargs)

class SampleForm(ModelForm):
    sample_datetime = forms.DateTimeField(label="Sample Created Datetime", widget=DateTimeInput(), initial=timezone.localtime(timezone.now()))
    class Meta:
        model = Sample
        fields = ['musicsampleid', 'patientid', 'sample_location', 'sample_type', 'sample_datetime', 'sample_comments']
        widgets = {
            'sample_datetime': DateTimeInput(),
        }
        labels = {
            'musicsampleid': "Sample ID",
            'patientid': "Patient ID",
            'sample_location': "Sample Location",
            'sample_type': "Sample Type",
            'sample_comments': "Comments",
        }

class CheckoutForm(ModelForm):
    class Meta:
        model = Sample
        fields = ['sample_location']
        labels = { 'sample_location': "Sample Location" }

