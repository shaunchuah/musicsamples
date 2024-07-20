from django import forms
from django.forms import ModelForm
from django.utils import timezone

from app.choices import (
    BIOPSY_INFLAMED_STATUS_CHOICES,
    BIOPSY_LOCATION_CHOICES,
    HAEMOLYSIS_REFERENCE_CHOICES,
    SAMPLE_TYPE_CHOICES,
    SAMPLE_VOLUME_UNIT_CHOICES,
    StudyNameChoices,
)
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
            "study_name",
            "sample_id",
            "sample_location",
            "sample_sublocation",
            "patient_id",
            "sample_type",
            "haemolysis_reference",
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
            "study_name": forms.Select(choices=StudyNameChoices.choices),
            "sample_type": forms.Select(choices=SAMPLE_TYPE_CHOICES),
            "sample_datetime": DateTimeInput(),
            "sample_volume_units": forms.Select(
                choices=SAMPLE_VOLUME_UNIT_CHOICES, attrs={"class": "form-control"}
            ),
            "frozen_datetime": DateTimeInput(),
            "haemolysis_reference": forms.Select(choices=HAEMOLYSIS_REFERENCE_CHOICES),
            "biopsy_location": forms.Select(choices=BIOPSY_LOCATION_CHOICES),
            "biopsy_inflamed_status": forms.Select(
                choices=BIOPSY_INFLAMED_STATUS_CHOICES
            ),
        }
        labels = {
            "study_name": "Study Name*",
            "sample_id": "Sample ID*",
            "patient_id": "Patient ID*",
            "sample_datetime": "Sampling Datetime*",
            "sample_location": "Sample Location*",
            "sample_sublocation": "Sample Sublocation",
            "sample_type": "Sample Type*",
            "sample_comments": "Comments",
            "sample_volume": "Volume Remaining (est.)",
            "sample_volume_units": "Sample Volume Units",
            "freeze_thaw_count": "No. of Freeze-Thaw Cycles",
            "haemolysis_reference": "Haemolysis Reference Palette",
            "biopsy_location": "Biopsy Location",
            "biopsy_inflamed_status": "Biopsy Inflamed Status",
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


class DeleteForm(ModelForm):
    class Meta:
        model = Sample
        fields = ["is_deleted"]
        labels = {"is_deleted": "Confirm delete?"}


class RestoreForm(ModelForm):
    class Meta:
        model = Sample
        fields = ["is_deleted"]
        labels = {"is_deleted": "Uncheck to restore"}


class FullyUsedForm(ModelForm):
    class Meta:
        model = Sample
        fields = ["is_fully_used"]
        labels = {"is_fully_used": "Mark sample as fully used?"}


class ReactivateForm(ModelForm):
    class Meta:
        model = Sample
        fields = ["is_fully_used"]
        labels = {"is_fully_used": "Uncheck to reactivate"}
