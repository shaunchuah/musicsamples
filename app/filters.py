import django_filters

from app.choices import SampleTypeChoices, SexChoices, StudyCenterChoices, StudyGroupChoices, StudyNameChoices
from app.models import DataStore, Sample


class SampleFilter(django_filters.FilterSet):
    study_name = django_filters.ChoiceFilter(label="Study Name", choices=StudyNameChoices.choices)
    sample_location = django_filters.AllValuesFilter(label="Sample Location")
    study_id__name = django_filters.AllValuesFilter(label="Study ID")
    sample_sublocation = django_filters.AllValuesFilter(label="Sample Sublocation")
    sample_type = django_filters.ChoiceFilter(label="Sample Type", choices=SampleTypeChoices.choices)
    is_used = django_filters.BooleanFilter(label="Used Samples?")
    sample_datetime = django_filters.DateFromToRangeFilter(
        widget=django_filters.widgets.RangeWidget(attrs={"type": "date"}),
        label="Sample Date Range",
    )
    sample_comments = django_filters.CharFilter(lookup_expr="icontains", label="Sample Comments")
    sample_volume = django_filters.NumberFilter(label="Sample Volume")
    study_id__study_group = django_filters.ChoiceFilter(label="Study Group", choices=StudyGroupChoices.choices)
    study_id__study_center = django_filters.ChoiceFilter(label="Study Center", choices=StudyCenterChoices.choices)
    study_id__sex = django_filters.ChoiceFilter(label="Biological Sex", choices=SexChoices.choices)

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
        ]


class DataStoreFilter(django_filters.FilterSet):
    study_id__name = django_filters.AllValuesFilter(label="Study ID")
    study_id__study_group = django_filters.ChoiceFilter(label="Study Group", choices=StudyGroupChoices.choices)
    study_id__study_center = django_filters.ChoiceFilter(label="Study Center", choices=StudyCenterChoices.choices)
    study_id__sex = django_filters.ChoiceFilter(label="Biological Sex", choices=SexChoices.choices)

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
