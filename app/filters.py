import django_filters

from app.choices import SampleTypeChoices, StudyNameChoices
from app.models import Sample


class SampleFilter(django_filters.FilterSet):
    study_name = django_filters.ChoiceFilter(
        label="Study Name", choices=StudyNameChoices.choices
    )
    patient_id = django_filters.AllValuesFilter(label="Patient ID")
    sample_location = django_filters.AllValuesFilter(label="Sample Location")
    sample_sublocation = django_filters.AllValuesFilter(label="Sample Sublocation")
    sample_type = django_filters.ChoiceFilter(
        label="Sample Type", choices=SampleTypeChoices.choices
    )
    is_used = django_filters.BooleanFilter(label="Used Samples?")
    sample_datetime = django_filters.DateFromToRangeFilter(
        widget=django_filters.widgets.RangeWidget(attrs={"type": "date"}),
        label="Sample Date Range",
    )
    sample_comments = django_filters.CharFilter(
        lookup_expr="icontains", label="Sample Comments"
    )
    sample_volume = django_filters.NumberFilter(label="Sample Volume")

    class Meta:
        model = Sample
        fields = [
            "study_name",
            "patient_id",
            "sample_location",
            "sample_sublocation",
            "sample_type",
            "is_used",
            "music_timepoint",
            "marvel_timepoint",
            "sample_comments",
            "sample_volume",
            "sample_datetime",
        ]
