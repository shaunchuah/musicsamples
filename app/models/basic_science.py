from django.conf import settings
from django.db import models
from simple_history.models import HistoricalRecords

from app.choices import (
    BasicScienceBoxTypeChoices,
    BasicScienceGroupChoices,
    BasicScienceSampleTypeChoices,
    ColumnChoices,
    DepthChoices,
    FreezerLocationChoices,
    RowChoices,
    SpeciesChoices,
    TissueTypeChoices,
)


class ExperimentalID(models.Model):
    name = models.CharField(max_length=200, unique=True)  # e.g., "EXP-001"
    description = models.TextField(blank=True, null=True)
    date = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.name


class BasicScienceSampleType(models.Model):
    name = models.CharField(max_length=200, choices=BasicScienceSampleTypeChoices.choices, unique=True)
    label = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.label if self.label else self.name


class TissueType(models.Model):
    name = models.CharField(max_length=200, choices=TissueTypeChoices.choices, unique=True)
    label = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.label if self.label else self.name


class BasicScienceBox(models.Model):
    # Core fields
    basic_science_group = models.CharField(max_length=200, choices=BasicScienceGroupChoices.choices)
    box_id = models.CharField(max_length=200, unique=True)
    box_type = models.CharField(max_length=200, choices=BasicScienceBoxTypeChoices.choices)
    species = models.CharField(max_length=100, choices=SpeciesChoices.choices)

    # Location and metadata
    location = models.CharField(max_length=200, choices=FreezerLocationChoices.choices)
    row = models.CharField(max_length=10, choices=RowChoices.choices, blank=True, null=True)
    column = models.CharField(max_length=10, choices=ColumnChoices.choices, blank=True, null=True)
    depth = models.CharField(max_length=10, choices=DepthChoices.choices, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

    # Contents (many-to-many for flexibility)
    experimental_ids = models.ManyToManyField(ExperimentalID, related_name="boxes")
    sample_types = models.ManyToManyField(BasicScienceSampleType, related_name="boxes")
    tissue_types = models.ManyToManyField(TissueType, related_name="boxes")

    is_used = models.BooleanField(default=False)

    # Tracking
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, related_name="created_boxes"
    )
    last_modified = models.DateTimeField(auto_now=True)
    last_modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, related_name="last_modified_boxes"
    )

    history = HistoricalRecords()

    def __str__(self):
        return f"{self.box_id} ({self.box_type})"

    class Meta:
        ordering = ["-created"]
        verbose_name_plural = "Basic Science Boxes"
