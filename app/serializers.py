from rest_framework import serializers
from .models import Sample


class SampleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Sample
        fields = [
            "sample_id",
            "sample_location",
            "sample_sublocation",
        ]
        lookup_field = "sample_id"


class SampleIsFullyUsedSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Sample
        fields = [
            "sample_id",
            "is_fully_used",
        ]
        lookup_field = "sample_id"


class MultipleSampleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Sample
        fields = [
            "sample_id",
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
        lookup_field = "sample_id"


class SampleExportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sample
        fields = [
            "sample_id",
            "patientid",
            "sample_location",
            "sample_type",
            "sample_datetime",
            "sample_comments",
            "processing_datetime",
            "sample_volume",
            "sample_volume_units",
            "freeze_thaw_count",
            "sample_sublocation",
            "is_fully_used",
            "haemolysis_reference",
            "biopsy_location",
            "biopsy_inflamed_status",
            "created_by",
            "last_modified_by",
            "created",
            "last_modified",
        ]
        lookup_field = "sample_id"
