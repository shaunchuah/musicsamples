from rest_framework import serializers
from .models import Sample


class SampleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Sample
        fields = [
            "musicsampleid",
            "sample_location",
            "sample_sublocation",
        ]
        lookup_field = "musicsampleid"


class SampleIsFullyUsedSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Sample
        fields = [
            "musicsampleid",
            "is_fully_used",
        ]
        lookup_field = "musicsampleid"


class MultipleSampleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Sample
        fields = [
            "musicsampleid",
            "sample_location",
            "sample_sublocation",
            "patientid",
            "sample_type",
            "haemolysis_reference",
            "biopsy_location",
            "biopsy_inflamed_status",
            "sample_datetime",
            "processing_datetime",
            "sample_comments",
            "sample_volume",
            "sample_volume_units",
            "freeze_thaw_count",
        ]
        lookup_field = "musicsampleid"
