import django_filters
from django.db import models
from django_filters.widgets import RangeWidget

from app.choices import (
    BasicScienceBoxTypeChoices,
    BasicScienceGroupChoices,
    ColumnChoices,
    DepthChoices,
    FreezerLocationChoices,
    RowChoices,
    SampleTypeChoices,
    SexChoices,
    StudyCenterChoices,
    StudyGroupChoices,
    StudyNameChoices,
)
from app.models import BasicScienceBox, BasicScienceSampleType, DataStore, ExperimentalID, Sample, TissueType


class SampleFilter(django_filters.FilterSet):
    study_name = django_filters.ChoiceFilter(label="Study Name", choices=StudyNameChoices.choices)
    sample_location = django_filters.AllValuesFilter(label="Sample Location")
    study_id__name = django_filters.AllValuesFilter(label="Study ID")
    sample_sublocation = django_filters.AllValuesFilter(label="Sample Sublocation")
    sample_type = django_filters.ChoiceFilter(label="Sample Type", choices=SampleTypeChoices.choices)
    is_used = django_filters.BooleanFilter(label="Used Samples?")
    sample_datetime = django_filters.DateFromToRangeFilter(
        widget=RangeWidget(attrs={"type": "date"}),
        label="Sample Date Range",
    )
    sample_comments = django_filters.CharFilter(lookup_expr="icontains", label="Sample Comments")
    sample_volume = django_filters.NumberFilter(label="Sample Volume")
    study_id__study_group = django_filters.ChoiceFilter(label="Study Group", choices=StudyGroupChoices.choices)
    study_id__study_center = django_filters.ChoiceFilter(label="Study Center", choices=StudyCenterChoices.choices)
    study_id__sex = django_filters.ChoiceFilter(label="Biological Sex", choices=SexChoices.choices)
    study_id__genotype_data_available = django_filters.BooleanFilter(label="Genotype Data Available")
    study_id__nod2_mutation_present = django_filters.BooleanFilter(label="NOD2 Mutation Present")
    study_id__il23r_mutation_present = django_filters.BooleanFilter(label="IL23R Mutation Present")
    endoscopic_mucosal_healing_at_3_6_months = django_filters.BooleanFilter(
        label="Endoscopic Mucosal Healing at 3-6 Months",
        method="filter_endoscopic_mucosal_healing_at_3_6_months",
    )
    endoscopic_mucosal_healing_at_12_months = django_filters.BooleanFilter(
        label="Endoscopic Mucosal Healing at 12 Months",
        method="filter_endoscopic_mucosal_healing_at_12_months",
    )

    def filter_endoscopic_mucosal_healing_at_3_6_months(self, queryset, name, value):
        # GI-DAMPs: by study_id + sample_date
        gidamps = queryset.filter(
            study_name__iexact="gidamps",
            study_id__clinical_data__sample_date=models.F("sample_datetime__date"),
            study_id__clinical_data__endoscopic_mucosal_healing_at_3_6_months=value,
        )
        # MUSIC: by study_id + music_timepoint
        music = queryset.filter(
            study_name__in=["music", "mini_music"],
            study_id__clinical_data__music_timepoint=models.F("music_timepoint"),
            study_id__clinical_data__endoscopic_mucosal_healing_at_3_6_months=value,
        )
        # Others: fallback to study_id + sample_date
        others = queryset.exclude(study_name__in=["gidamps", "music", "mini_music"]).filter(
            study_id__clinical_data__sample_date=models.F("sample_datetime__date"),
            study_id__clinical_data__endoscopic_mucosal_healing_at_3_6_months=value,
        )
        return gidamps | music | others

    def filter_endoscopic_mucosal_healing_at_12_months(self, queryset, name, value):
        gidamps = queryset.filter(
            study_name__iexact="gidamps",
            study_id__clinical_data__sample_date=models.F("sample_datetime__date"),
            study_id__clinical_data__endoscopic_mucosal_healing_at_12_months=value,
        )
        music = queryset.filter(
            study_name__in=["music", "mini_music"],
            study_id__clinical_data__music_timepoint=models.F("music_timepoint"),
            study_id__clinical_data__endoscopic_mucosal_healing_at_12_months=value,
        )
        others = queryset.exclude(study_name__in=["gidamps", "music", "mini_music"]).filter(
            study_id__clinical_data__sample_date=models.F("sample_datetime__date"),
            study_id__clinical_data__endoscopic_mucosal_healing_at_12_months=value,
        )
        return gidamps | music | others

    class Meta:
        model = Sample
        fields = [
            "study_name",
            "study_id__name",
            "sample_location",
            "sample_sublocation",
            "sample_type",
            "is_used",
            "music_timepoint",
            "marvel_timepoint",
            "sample_comments",
            "sample_volume",
            "sample_datetime",
            "study_id__study_group",
            "study_id__study_center",
            "study_id__sex",
            "study_id__genotype_data_available",
            "study_id__nod2_mutation_present",
            "study_id__il23r_mutation_present",
            "endoscopic_mucosal_healing_at_3_6_months",
            "endoscopic_mucosal_healing_at_12_months",
        ]


class DataStoreFilter(django_filters.FilterSet):
    study_id__name = django_filters.AllValuesFilter(label="Study ID")
    study_id__study_group = django_filters.ChoiceFilter(label="Study Group", choices=StudyGroupChoices.choices)
    study_id__study_center = django_filters.ChoiceFilter(label="Study Center", choices=StudyCenterChoices.choices)
    study_id__sex = django_filters.ChoiceFilter(label="Biological Sex", choices=SexChoices.choices)
    study_id__genotype_data_available = django_filters.BooleanFilter(label="Genotype Data Available")
    study_id__nod2_mutation_present = django_filters.BooleanFilter(label="NOD2 Mutation Present")
    study_id__il23r_mutation_present = django_filters.BooleanFilter(label="IL23R Mutation Present")

    class Meta:
        model = DataStore
        fields = [
            "category",
            "study_name",
            "study_id__name",
            "music_timepoint",
            "marvel_timepoint",
            "study_id__study_group",
            "study_id__study_center",
            "study_id__sex",
            "study_id__genotype_data_available",
            "study_id__nod2_mutation_present",
            "study_id__il23r_mutation_present",
        ]


class BasicScienceBoxFilter(django_filters.FilterSet):
    basic_science_group = django_filters.ChoiceFilter(
        label="Basic Science Group", choices=BasicScienceGroupChoices.choices
    )
    box_type = django_filters.ChoiceFilter(label="Box Type", choices=BasicScienceBoxTypeChoices.choices)
    location = django_filters.ChoiceFilter(label="Location", choices=FreezerLocationChoices.choices)
    row = django_filters.ChoiceFilter(label="Row", choices=RowChoices.choices)
    column = django_filters.ChoiceFilter(label="Column", choices=ColumnChoices.choices)
    depth = django_filters.ChoiceFilter(label="Depth", choices=DepthChoices.choices)
    experimental_ids = django_filters.ModelMultipleChoiceFilter(
        label="Experimental IDs", queryset=ExperimentalID.objects.all(), method="filter_experimental_ids"
    )
    experimental_ids_date = django_filters.DateFromToRangeFilter(
        label="Experimental IDs Date Range",
        widget=RangeWidget(attrs={"type": "date"}),
        method="filter_experimental_ids_date",
    )
    sample_types = django_filters.ModelMultipleChoiceFilter(
        label="Sample Types", queryset=BasicScienceSampleType.objects.all(), method="filter_sample_types"
    )
    tissue_types = django_filters.ModelMultipleChoiceFilter(
        label="Tissue Types", queryset=TissueType.objects.all(), method="filter_tissue_types"
    )
    is_used = django_filters.BooleanFilter(label="Used?")

    def filter_experimental_ids(self, queryset, name, value):
        if value:
            return queryset.filter(experimental_ids__in=value)
        return queryset

    def filter_experimental_ids_date(self, queryset, name, value):
        if value:
            if value.start:
                queryset = queryset.filter(experimental_ids__date__gte=value.start)
            if value.stop:
                queryset = queryset.filter(experimental_ids__date__lte=value.stop)
        return queryset

    def filter_sample_types(self, queryset, name, value):
        if value:
            return queryset.filter(sample_types__in=value)
        return queryset

    def filter_tissue_types(self, queryset, name, value):
        if value:
            return queryset.filter(tissue_types__in=value)
        return queryset

    class Meta:
        model = BasicScienceBox
        fields = [
            "basic_science_group",
            "box_type",
            "location",
            "row",
            "column",
            "depth",
            "is_used",
        ]
