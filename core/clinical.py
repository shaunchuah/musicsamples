# /Users/chershiongchuah/Developer/musicsamples/core/clinical.py
# This module contains functions for retrieving clinical data for samples.
# It handles study-specific matching logic for clinical data queries.

from django.db import models
from django.db.models import Case, OuterRef, Subquery, When
from django.db.models.functions import Lower

from app.models import ClinicalData


def get_sample_with_clinical_data(sample):
    """
    Get clinical data for a specific sample based on study type-specific matching
    """
    # First check if this sample has a study_id
    if not sample.study_id:
        return None

    study_name = sample.study_id.study_name.lower() if sample.study_id.study_name else ""
    sample_date = sample.sample_datetime.date() if sample.sample_datetime else None

    try:
        # Different lookup strategy based on study name
        if "gidamps" in study_name:
            # GI-DAMPs uses study_id and sample_date
            if not sample_date:
                return None

            clinical_data = ClinicalData.objects.get(study_id=sample.study_id, sample_date=sample_date)

        elif "music" in study_name:
            # MUSIC and Mini-MUSIC use study_id and music_timepoint
            if not sample.music_timepoint:
                # Try sample_date as fallback if available
                if sample_date:
                    clinical_data = ClinicalData.objects.get(study_id=sample.study_id, sample_date=sample_date)
                else:
                    return None
            else:
                clinical_data = ClinicalData.objects.get(
                    study_id=sample.study_id, music_timepoint=sample.music_timepoint
                )

        else:
            # Default to sample_date for unknown studies
            if not sample_date:
                return None

            clinical_data = ClinicalData.objects.get(study_id=sample.study_id, sample_date=sample_date)

        return clinical_data

    except ClinicalData.DoesNotExist:
        return None


def get_samples_with_clinical_data(queryset):
    """
    Annotate a queryset of samples with clinical data using study-specific matching
    """
    # First, annotate with sample_date for joining
    samples_with_date = queryset.annotate(
        sample_date=models.functions.TruncDate("sample_datetime"), study_name_lower=Lower("study_id__study_name")
    )

    # Create a conditional subquery based on study name
    # For GI-DAMPs - use study_id and sample_date
    gidamps_clinical_data = ClinicalData.objects.filter(
        study_id=OuterRef("study_id"), sample_date=OuterRef("sample_date")
    )

    # For MUSIC/Mini-MUSIC - use study_id and music_timepoint
    music_clinical_data = ClinicalData.objects.filter(
        study_id=OuterRef("study_id"), music_timepoint=OuterRef("music_timepoint")
    )

    # Default - use study_id and sample_date
    default_clinical_data = ClinicalData.objects.filter(
        study_id=OuterRef("study_id"), sample_date=OuterRef("sample_date")
    )

    # Annotate with clinical data fields using conditional lookups
    samples_with_clinical = samples_with_date.annotate(
        crp=Case(
            When(study_name_lower__contains="gidamps", then=Subquery(gidamps_clinical_data.values("crp")[:1])),
            When(study_name_lower__contains="music", then=Subquery(music_clinical_data.values("crp")[:1])),
            default=Subquery(default_clinical_data.values("crp")[:1]),
        ),
        calprotectin=Case(
            When(
                study_name_lower__contains="gidamps", then=Subquery(gidamps_clinical_data.values("calprotectin")[:1])
            ),
            When(study_name_lower__contains="music", then=Subquery(music_clinical_data.values("calprotectin")[:1])),
            default=Subquery(default_clinical_data.values("calprotectin")[:1]),
        ),
        # Add more fields as needed using the same pattern
        endoscopic_mucosal_healing_at_3_6_months=Case(
            When(
                study_name_lower__contains="music",
                then=Subquery(music_clinical_data.values("endoscopic_mucosal_healing_at_3_6_months")[:1]),
            )
        ),
        endoscopic_mucosal_healing_at_12_months=Case(
            When(
                study_name_lower__contains="music",
                then=Subquery(music_clinical_data.values("endoscopic_mucosal_healing_at_12_months")[:1]),
            )
        ),
    )

    return samples_with_clinical
