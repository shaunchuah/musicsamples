from django.db import models
from simple_history.models import HistoricalRecords

from app.choices import (
    BiopsyInflamedStatusChoices,
    BiopsyLocationChoices,
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

        # Suspend form validation until all samples have been allocated timepoints
        # if (
        #     self.study_name == StudyNameChoices.MUSIC
        #     or self.study_name == StudyNameChoices.MINI_MUSIC
        # ):
        #     if self.music_timepoint is None or self.music_timepoint == "":
        #         raise ValidationError(
        #             {
        #                 "music_timepoint": "Music Timepoint must be filled for MUSIC and Mini-MUSIC studies."
        #             }
        #         )

    def __str__(self):
        return self.sample_id

    def natural_key(self):
        return self.sample_id

    class Meta:
        ordering = ["-created"]
