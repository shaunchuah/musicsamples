import pathlib
from typing import Optional

from azure.core.exceptions import ResourceNotFoundError
from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from guardian.shortcuts import assign_perm
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
    SexChoices,
    StudyCenterChoices,
    StudyGroupChoices,
    StudyNameChoices,
)


class StudyIdentifier(models.Model):
    name = models.CharField(max_length=200, unique=True)
    study_name = models.CharField(max_length=200, choices=StudyNameChoices.choices, blank=True, null=True)
    study_center = models.CharField(
        max_length=200,
        choices=StudyCenterChoices.choices,
        blank=True,
        null=True,
    )
    study_group = models.CharField(max_length=200, choices=StudyGroupChoices.choices, blank=True, null=True)
    sex = models.CharField(max_length=10, choices=SexChoices.choices, blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)
    genotype_data_available = models.BooleanField(default=False)
    nod2_mutation_present = models.BooleanField(default=False)
    il23r_mutation_present = models.BooleanField(default=False)

    history = HistoricalRecords()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Study Identifier"
        verbose_name_plural = "Study Identifiers"
        ordering = ["name"]


class Sample(models.Model):
    study_name = models.CharField(max_length=200, choices=StudyNameChoices.choices)
    study_id = models.ForeignKey(
        StudyIdentifier, on_delete=models.PROTECT, related_name="samples", null=True, blank=True
    )
    sample_id = models.CharField(max_length=200, unique=True)
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


def file_generate_name(original_file_name: str, study_name: str, study_id: Optional[str] = None) -> str:
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
    study_id = models.ForeignKey(
        StudyIdentifier, on_delete=models.PROTECT, related_name="files", null=True, blank=True
    )
    music_timepoint = models.CharField(max_length=50, blank=True, null=True, choices=MusicTimepointChoices.choices)
    marvel_timepoint = models.CharField(max_length=50, blank=True, null=True, choices=MarvelTimepointChoices.choices)
    sampling_date = models.DateField(blank=True, null=True)  # for merging GI-DAMPs
    comments = models.TextField(blank=True, null=True)

    file = models.FileField(upload_to=file_upload_path, blank=True, null=True)

    file_type = models.CharField(max_length=255, blank=True)  # File Extension
    original_file_name = models.TextField(blank=True)
    formatted_file_name = models.TextField(blank=True)

    upload_finished_at = models.DateTimeField(blank=True, null=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, related_name="uploaded_files"
    )

    history = HistoricalRecords()

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
        try:
            return self.file.size
        except ResourceNotFoundError:
            return None

    def __str__(self):
        return self.formatted_file_name

    class Meta:
        ordering = ["-upload_finished_at"]
        permissions = (("delete_own_datastore", "Can delete own datastore"),)


@receiver(post_save, sender=DataStore)
def set_permission(sender, instance, created, **kwargs):
    if created and instance.uploaded_by:
        assign_perm("delete_own_datastore", instance.uploaded_by, instance)
        assign_perm("app.view_datastore", instance.uploaded_by, instance)


class ClinicalData(models.Model):
    study_id = models.ForeignKey(StudyIdentifier, null=True, on_delete=models.PROTECT, related_name="clinical_data")
    sample_date = models.DateField(null=True)
    music_timepoint = models.CharField(max_length=50, null=True, blank=True, choices=MusicTimepointChoices.choices)

    # Clinical markers
    crp = models.FloatField(null=True, blank=True)
    calprotectin = models.FloatField(null=True, blank=True)
    endoscopic_mucosal_healing_at_3_6_months = models.BooleanField(
        null=True, blank=True, verbose_name="Endoscopic mucosal healing at 3-6 months"
    )
    endoscopic_mucosal_healing_at_12_months = models.BooleanField(
        null=True, blank=True, verbose_name="Endoscopic mucosal healing at 12 months"
    )

    # Additional fields...
    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    class Meta:
        # Add a constraint to ensure we have either sample_date or music_timepoint
        constraints = [
            models.CheckConstraint(
                check=(models.Q(sample_date__isnull=False) | models.Q(music_timepoint__isnull=False)),
                name="clinical_data_has_date_or_timepoint",
            ),
            # Unique constraints for different study types
            models.UniqueConstraint(
                fields=["study_id", "sample_date"],
                condition=models.Q(music_timepoint__isnull=True),
                name="unique_study_id_sample_date",
            ),
            models.UniqueConstraint(
                fields=["study_id", "music_timepoint"],
                condition=models.Q(sample_date__isnull=True),
                name="unique_study_id_music_timepoint",
            ),
        ]
