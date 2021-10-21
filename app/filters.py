import django_filters

from .models import Sample


class SampleFilter(django_filters.FilterSet):
    patient_id = django_filters.CharFilter(lookup_expr="iexact")
    sample_location = django_filters.CharFilter(lookup_expr="iexact")
    sample_sublocation = django_filters.CharFilter(lookup_expr="iexact")
    sample_type = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = Sample
        fields = [
            "patient_id",
            "sample_location",
            "sample_sublocation",
            "sample_type",
            "is_deleted",
            "is_fully_used",
        ]
