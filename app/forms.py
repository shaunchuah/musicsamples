from django import forms
from django.forms import ModelForm
from django.utils import timezone

from app.models import Sample


class DateTimeInput(forms.DateTimeInput):
    # Set default sample creation time to the time
    # the user is accessing the add new sample page
    input_type = "datetime-local"

    def __init__(self, **kwargs):
        kwargs["format"] = "%Y-%m-%dT%H:%M"
        super().__init__(**kwargs)


def currentTime():
    time = timezone.localtime(timezone.now())
    return time


class SampleForm(ModelForm):
    # Main sample registration form
    processing_datetime = forms.DateTimeField(
        label="Processing Datetime",
        widget=DateTimeInput(),
        initial=currentTime,
        required=False,
    )

    class Meta:
        model = Sample
        fields = [
            "sample_id",
            "sample_location",
            "sample_sublocation",
            "study_name",
            "music_timepoint",
            "marvel_timepoint",
            "patient_id",
            "sample_type",
            "qubit_cfdna_ng_ul",
            "haemolysis_reference",
            "paraffin_block_key",
            "biopsy_location",
            "biopsy_inflamed_status",
            "sample_datetime",
            "processing_datetime",
            "frozen_datetime",
            "sample_comments",
            "sample_volume",
            "sample_volume_units",
            "freeze_thaw_count",
        ]
        widgets = {
            "sample_datetime": DateTimeInput(),
            "frozen_datetime": DateTimeInput(),
        }
        labels = {
            "study_name": "Study Name*",
            "music_timepoint": "Music Timepoint",
            "marvel_timepoint": "Marvel Timepoint",
            "sample_id": "Sample ID*",
            "patient_id": "Patient ID*",
            "sample_datetime": "Sampling Datetime*",
            "sample_location": "Sample Location*",
            "sample_sublocation": "Sample Sublocation",
            "sample_type": "Sample Type*",
            "qubit_cfdna_ng_ul": "Qubit (ng/uL:)",
            "sample_comments": "Comments",
            "sample_volume": "Volume Remaining (est.)",
            "sample_volume_units": "Sample Volume Units",
            "freeze_thaw_count": "No. of Freeze-Thaw Cycles",
            "haemolysis_reference": "Haemolysis Reference Palette",
            "biopsy_location": "Biopsy Location",
            "biopsy_inflamed_status": "Biopsy Inflamed Status",
            "paraffin_block_key": "Paraffin Block Key",
            "frozen_datetime": "Frozen Datetime (If Applicable)",
        }


class CheckoutForm(ModelForm):
    class Meta:
        model = Sample
        fields = ["sample_location", "sample_sublocation"]
        labels = {
            "sample_location": "Sample Location",
            "sample_sublocation": "Sample Sublocation",
        }


class UsedForm(ModelForm):
    class Meta:
        model = Sample
        fields = ["is_used"]
        labels = {"is_used": "Mark sample as used?"}


class ReactivateForm(ModelForm):
    class Meta:
        model = Sample
        fields = ["is_used"]
        labels = {"is_used": "Uncheck to reactivate"}
