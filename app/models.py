import datetime
import pathlib

from django.conf import settings
from django.db import models
from simple_history.models import HistoricalRecords

from app.choices import (
    BiopsyInflamedStatusChoices,
    BiopsyLocationChoices,
    FileCategoryChoices,
    HaemolysisReferenceChoices,
    MarvelTimepointChoices,
    MusicTimepointChoices,
    SampleTypeChoices,
    SampleVolumeUnitChoices,
    StudyNameChoices,
)


class Sample(models.Model):
    study_name = models.CharField(max_length=200, choices=StudyNameChoices.choices)

    sample_id = models.CharField(max_length=200, unique=True)
    patient_id = models.CharField(max_length=200)
    sample_location = models.CharField(max_length=200)
    sample_sublocation = models.CharField(max_length=200, blank=True, null=True)
    sample_type = models.CharField(max_length=200, choices=SampleTypeChoices.choices)
    sample_datetime = models.DateTimeField()
    sample_comments = models.TextField(blank=True, null=True)

    is_used = models.BooleanField(default=False)

    music_timepoint = models.CharField(max_length=50, blank=True, null=True, choices=MusicTimepointChoices.choices)
    marvel_timepoint = models.CharField(max_length=50, blank=True, null=True, choices=MarvelTimepointChoices.choices)

    processing_datetime = models.DateTimeField(blank=True, null=True)
    frozen_datetime = models.DateTimeField(blank=True, null=True)
    sample_volume = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    sample_volume_units = models.CharField(
        max_length=30, blank=True, null=True, choices=SampleVolumeUnitChoices.choices
    )
    freeze_thaw_count = models.IntegerField(default=0)
    haemolysis_reference = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        choices=HaemolysisReferenceChoices.choices,
    )
    biopsy_location = models.CharField(max_length=100, blank=True, null=True, choices=BiopsyLocationChoices.choices)
    biopsy_inflamed_status = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=BiopsyInflamedStatusChoices.choices,
    )
    qubit_cfdna_ng_ul = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    paraffin_block_key = models.CharField(max_length=10, blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=200)
    last_modified = models.DateTimeField(auto_now=True)
    last_modified_by = models.CharField(max_length=200)

    history = HistoricalRecords()

    def clean(self):
        self.sample_id = self.sample_id.upper()
        self.patient_id = self.patient_id.upper()

    def __str__(self):
        return self.sample_id

    def natural_key(self):
        return self.sample_id

    class Meta:
        ordering = ["-created"]


def file_upload_path(instance, filename):
    """
    Returns the path for Azure uploads
    In this case "category/<file>"
    """
    # Both filename and instance.file_name should have the same values
    return f"{instance.category}/{instance.formatted_file_name}"


def file_generate_name(original_file_name: str, study_name: str, study_id: str = None) -> str:
    """
    Takes filename, study_name and returns a formatted filename with unique hash
    """
    extension = pathlib.Path(original_file_name).suffix
    file_name = pathlib.Path(original_file_name).stem
    if not study_id:
        return f"{study_name}_{file_name}{extension}"
    return f"{study_name}_{study_id}_{file_name}{extension}"


class DataStore(models.Model):
    # Metadata Fields
    category = models.CharField(max_length=200, choices=FileCategoryChoices.choices)
    study_name = models.CharField(max_length=200, choices=StudyNameChoices.choices)
    patient_id = models.CharField(max_length=200, blank=True, null=True)
    music_timepoint = models.CharField(max_length=50, blank=True, null=True, choices=MusicTimepointChoices.choices)
    marvel_timepoint = models.CharField(max_length=50, blank=True, null=True, choices=MarvelTimepointChoices.choices)
    comments = models.TextField(blank=True, null=True)
    sample_id = models.ForeignKey(Sample, null=True, blank=True, on_delete=models.SET_NULL, related_name="files")

    file = models.FileField(upload_to=file_upload_path, blank=True, null=True)

    file_type = models.CharField(max_length=255, blank=True)  # File Extension
    original_file_name = models.TextField(blank=True)
    formatted_file_name = models.TextField(blank=True)

    upload_finished_at = models.DateTimeField(blank=True, null=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, related_name="uploaded_files"
    )

    @property
    def is_valid(self):
        """
        We consider a file "valid" if the the datetime flag has value.
        """
        return bool(self.upload_finished_at)

    @property
    def url(self):
        if self.file:
            return self.file.url

    @property
    def size(self):
        if self.file:
            return self.file.size

    def __str__(self):
        return self.formatted_file_name

    def clean(self):
        if self.patient_id:
            self.patient_id = self.patient_id.upper()
        super().clean()

    def save(self, *args, **kwargs):
        if self.file:
            # This is the default django method
            # Takes the original file, saves the original file name,
            # generates a new file name and saves the file with the new name
            self.file_type = self.file.name.split(".")[-1]
            self.original_file_name = self.file.name
            self.formatted_file_name = file_generate_name(self.original_file_name, self.study_name, self.patient_id)
            self.file.name = self.formatted_file_name
            self.upload_finished_at = datetime.datetime.now()
        super().save(*args, **kwargs)
        # TODO: when doing asynchronous upload, we might need to generate the formatted url and file name

    class Meta:
        ordering = ["-upload_finished_at"]
