from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django import forms
from django.forms import ModelForm
from django.utils import timezone
from django_select2.forms import ModelSelect2MultipleWidget
from taggit.forms import TagWidget

from .models import Note, Sample
from .choices import (
    SAMPLE_TYPE_CHOICES,
    SAMPLE_VOLUME_UNIT_CHOICES,
    HAEMOLYSIS_REFERENCE_CHOICES,
    BIOPSY_LOCATION_CHOICES,
    BIOPSY_INFLAMED_STATUS_CHOICES,
)


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
    # sample_datetime = forms.DateTimeField(
    #     label="Sampling Datetime*",
    #     widget=DateTimeInput(),
    # )

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
            "patient_id",
            "sample_type",
            "haemolysis_reference",
            "biopsy_location",
            "biopsy_inflamed_status",
            "sample_datetime",
            "processing_datetime",
            "sample_comments",
            "sample_volume",
            "sample_volume_units",
            "freeze_thaw_count",
        ]
        widgets = {
            "sample_type": forms.Select(choices=SAMPLE_TYPE_CHOICES),
            "sample_datetime": DateTimeInput(),
            "sample_volume_units": forms.Select(
                choices=SAMPLE_VOLUME_UNIT_CHOICES, attrs={"class": "form-control"}
            ),
            "haemolysis_reference": forms.Select(choices=HAEMOLYSIS_REFERENCE_CHOICES),
            "biopsy_location": forms.Select(choices=BIOPSY_LOCATION_CHOICES),
            "biopsy_inflamed_status": forms.Select(
                choices=BIOPSY_INFLAMED_STATUS_CHOICES
            ),
        }
        labels = {
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
        }


class CheckoutForm(ModelForm):
    # Quick update of sample location from home page
    class Meta:
        model = Sample
        fields = ["sample_location", "sample_sublocation"]
        labels = {
            "sample_location": "Sample Location",
            "sample_sublocation": "Sample Sublocation",
        }


class DeleteForm(ModelForm):
    # Soft deleting a sample
    class Meta:
        model = Sample
        fields = ["is_deleted"]
        labels = {"is_deleted": "Confirm delete?"}


class RestoreForm(ModelForm):
    # Restoring a soft deleted sample
    class Meta:
        model = Sample
        fields = ["is_deleted"]
        labels = {"is_deleted": "Uncheck to restore"}


class FullyUsedForm(ModelForm):
    # Marking a sample as fully used
    class Meta:
        model = Sample
        fields = ["is_fully_used"]
        labels = {"is_fully_used": "Mark sample as fully used?"}


class ReactivateForm(ModelForm):
    # Restoring a sample that was accidentally marked as fully used
    class Meta:
        model = Sample
        fields = ["is_fully_used"]
        labels = {"is_fully_used": "Uncheck to reactivate"}


#########################################################################
# NOTEFORMS  ############################################################
#########################################################################
# SELECT2 #####

# Create new note form
# Django select2 used to enable tagging of existing samples.
# Django taggit used for tagging of notes similar to blogging
# CKEditor Uploading widget used for adding of notes and supporting of file/image
# uploads - Suggest use an S3 backend to handle user media uploads.
# You can also disable this by switching the uploading widget for the standard one
#  - see django-ckeditor documentation.


class NoteForm(ModelForm):
    class Meta:
        model = Note
        fields = ["title", "content", "sample_tags", "tags", "is_public"]
        widgets = {
            "content": forms.CharField(widget=CKEditorUploadingWidget()),
            "tags": TagWidget(attrs={"data-role": "tagsinput"}),
            "is_public": forms.Select(choices=((False, "Private"), (True, "Shared"))),
            "sample_tags": ModelSelect2MultipleWidget(
                model=Sample, search_fields=["sample_id__icontains"]
            ),
        }
        labels = {
            "is_public": "Share settings:",
            "content": "",
        }


class NoteDeleteForm(ModelForm):
    # Soft deletion of notes. Restoration will probably have to be done
    # from the django admin panel unless you want to implement a restore
    # view similar to the above sample restoration methods.
    class Meta:
        model = Note
        fields = ["is_deleted"]
        labels = {"is_deleted": "Confirm delete?"}
