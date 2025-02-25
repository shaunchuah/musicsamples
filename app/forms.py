from django import forms
from django.forms import ModelForm
from django.utils import timezone
from django_select2 import forms as s2forms

from app.models import DataStore, Sample, StudyIdentifier


class DateInput(forms.DateInput):
    input_type = "date"


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
    study_id = forms.CharField(label="Study ID*", required=True)
    processing_datetime = forms.DateTimeField(
        label="Processing Datetime",
        widget=DateTimeInput(),
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
            "study_id",
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
            "study_id": "Study ID*",
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

    def clean(self):
        cleaned_data = super().clean()
        study_id_text = cleaned_data.get("study_id")
        if study_id_text:
            study_id_text = study_id_text.upper()
            study_identifier, created = StudyIdentifier.objects.get_or_create(name=study_id_text)
            cleaned_data["study_id"] = study_identifier
        return cleaned_data


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


class SampleSelectionWidget(s2forms.ModelSelect2MultipleWidget):
    search_fields = [
        "sample_id__icontains",
    ]


class DataStoreForm(ModelForm):
    study_id = forms.CharField(label="Associated Study ID (optional)", required=False)

    class Meta:
        model = DataStore
        fields = [
            "file",
            "category",
            "study_name",
            "music_timepoint",
            "marvel_timepoint",
            "study_id",
            "comments",
        ]
        labels = {
            "category": "Category*",
            "study_name": "Study Name*",
            "music_timepoint": "Music Timepoint",
            "marvel_timepoint": "Marvel Timepoint",
            "comments": "Comments",
        }

    def __init__(self, *args, **kwargs):
        super(DataStoreForm, self).__init__(*args, **kwargs)
        self.fields["file"].widget.attrs = {"class": "form-control-file custom-file-input"}

    def clean(self):
        cleaned_data = super().clean()
        study_id_text = cleaned_data.get("study_id")
        if study_id_text:
            study_id_text = study_id_text.upper()
            study_identifier, created = StudyIdentifier.objects.get_or_create(name=study_id_text)
            cleaned_data["study_id"] = study_identifier
        return cleaned_data


class DataStoreUpdateForm(ModelForm):
    class Meta:
        model = DataStore
        fields = [
            "music_timepoint",
            "marvel_timepoint",
            "comments",
        ]
        labels = {
            "music_timepoint": "Music Timepoint",
            "marvel_timepoint": "Marvel Timepoint",
            "comments": "Comments",
        }
