import django_filters

from .models import Sample
from .choices import SAMPLE_TYPE_CHOICES


class SampleFilter(django_filters.FilterSet):
    patient_id = django_filters.AllValuesFilter(label="Patient ID")
    sample_location = django_filters.AllValuesFilter(label="Sample Location")
    sample_sublocation = django_filters.AllValuesFilter(label="Sample Sublocation")
    sample_type = django_filters.ChoiceFilter(
        label="Sample Type", choices=SAMPLE_TYPE_CHOICES
    )
    is_fully_used = django_filters.BooleanFilter(label="Used Samples?")
    sample_datetime = django_filters.DateFromToRangeFilter(
        widget=django_filters.widgets.RangeWidget(attrs={"type": "date"}),
        label="Sample Date Range",
    )
    sample_comments = django_filters.CharFilter(
        lookup_expr="icontains", label="Sample Comments Contains"
    )
    sample_volume = django_filters.NumberFilter(label="Sample Volume")

    class Meta:
        model = Sample
        fields = [
            "patient_id",
            "sample_location",
            "sample_sublocation",
            "sample_type",
            "is_fully_used",
            "sample_datetime",
            "sample_comments",
            "sample_volume",
        ]
