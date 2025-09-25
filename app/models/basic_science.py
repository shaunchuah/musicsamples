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


class ExperimentalID(models.Model):
    basic_science_group = models.CharField(max_length=200, choices=BasicScienceGroupChoices.choices)
    name = models.CharField(max_length=200)  # e.g., "EXP-001"
    description = models.TextField(blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    sample_types = models.ManyToManyField(
        BasicScienceSampleType,
        related_name="experimental_ids",
        blank=True,
    )
    tissue_types = models.ManyToManyField(
        TissueType,
        related_name="experimental_ids",
        blank=True,
    )
    species = models.CharField(max_length=100, choices=SpeciesChoices.choices)

    # Tracking
    is_deleted = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="created_experimental_ids",
    )
    last_modified = models.DateTimeField(auto_now=True)
    last_modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="last_modified_experimental_ids",
    )

    history = HistoricalRecords()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["-created"]
        verbose_name_plural = "Experimental IDs"
        unique_together = [["basic_science_group", "name"]]


class BasicScienceBox(models.Model):
    # Core fields
    box_id = models.CharField(max_length=200, unique=True)
    box_type = models.CharField(max_length=200, choices=BasicScienceBoxTypeChoices.choices)

    # Location and metadata
    location = models.CharField(max_length=200, choices=FreezerLocationChoices.choices)
    row = models.CharField(max_length=10, choices=RowChoices.choices, blank=True, null=True)
    column = models.CharField(max_length=10, choices=ColumnChoices.choices, blank=True, null=True)
    depth = models.CharField(max_length=10, choices=DepthChoices.choices, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

    # Contents (many-to-many for flexibility)
    experimental_ids = models.ManyToManyField(ExperimentalID, related_name="boxes")

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
        return f"{self.box_id}"

    def distinct_sample_types(self):
        unique = {}
        for experimental_id in self.experimental_ids.all():
            for sample_type in experimental_id.sample_types.all():
                unique[sample_type.pk] = sample_type
        return list(unique.values())

    def distinct_tissue_types(self):
        unique = {}
        for experimental_id in self.experimental_ids.all():
            for tissue_type in experimental_id.tissue_types.all():
                unique[tissue_type.pk] = tissue_type
        return list(unique.values())

    def get_sample_type_labels(self):
        return [sample_type.label or sample_type.name for sample_type in self.distinct_sample_types()]

    def get_tissue_type_labels(self):
        return [tissue_type.label or tissue_type.name for tissue_type in self.distinct_tissue_types()]

    def basic_science_groups(self):
        """Return a sorted list of unique basic science group values for linked experiments."""
        groups = {experimental_id.basic_science_group for experimental_id in self.experimental_ids.all()}
        return sorted(groups)

    def get_basic_science_group_labels(self):
        return [BasicScienceGroupChoices(group).label for group in self.basic_science_groups()]

    @property
    def sample_type_labels_display(self):
        return ", ".join(self.get_sample_type_labels())

    @property
    def tissue_type_labels_display(self):
        return ", ".join(self.get_tissue_type_labels())

    @property
    def basic_science_groups_display(self):
        return ", ".join(self.get_basic_science_group_labels())

    class Meta:
        ordering = ["-created"]
        verbose_name_plural = "Basic Science Boxes"
