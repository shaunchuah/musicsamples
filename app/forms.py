from django import forms
from django.utils import timezone
from django.forms import ModelForm, modelformset_factory, formset_factory
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
        fields = ['musicsampleid', 'sample_type', 'patientid', 'sample_location', 'sample_datetime', 'sample_comments', 'processing_datetime', 'sample_volume', 'sample_volume_units', 'freeze_thaw_count', ]
        SAMPLE_VOLUME_UNIT_CHOICES = (
            ('', 'Select unit'),
            ('ml', 'ml'),
            ('ul', 'ul'),
        )
        widgets = {
            'sample_datetime': DateTimeInput(),
            'sample_volume_units': forms.Select(choices=SAMPLE_VOLUME_UNIT_CHOICES, attrs={'class': 'form-control'}),
            'processing_datetime': DateTimeInput(),
        }
        labels = {
            'musicsampleid': "Sample ID",
            'patientid': "Patient ID",
            'sample_location': "Sample Location",
            'sample_type': "Sample Type",
            'sample_datetime': "Sample Taken Datetime",
            'sample_comments': "Comments",
            'processing_datetime': "Processing Datetime",
            'sample_volume': "Sample Volume",
            'sample_volume_units': "Sample Volume Units",
            'freeze_thaw_count': "Number of Freeze-Thaw Cycles",            
        }

class CheckoutForm(ModelForm):
    class Meta:
        model = Sample
        fields = ['sample_location']
        labels = { 'sample_location': "Sample Location" }

class DeleteForm(ModelForm):
    class Meta:
        model = Sample
        fields = ['is_deleted']
        labels = { 'is_deleted': "Confirm Delete?" }

class RestoreForm(ModelForm):
    class Meta:
        model = Sample
        fields = ['is_deleted']
        labels = { 'is_deleted': "Uncheck to Restore" }

#SampleFormSet = modelformset_factory(Sample, fields=('musicsampleid', 'patientid', 'sample_location', 'sample_type', 'sample_datetime', 'sample_comments'), extra=2)
SampleFormSet = formset_factory(SampleForm, extra=1)