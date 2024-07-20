from rest_framework import serializers

from app.models import Sample


class SampleSerializer(serializers.ModelSerializer):
    """
    Serializer for updating sample locations
    """

    class Meta:
        model = Sample
        fields = [
            "sample_id",
            "sample_location",
            "sample_sublocation",
        ]
        lookup_field = "sample_id"


class SampleIsFullyUsedSerializer(serializers.ModelSerializer):
    """
    Serializer for marking samples as used
    """

    class Meta:
        model = Sample
        fields = [
            "sample_id",
            "is_fully_used",
        ]
        lookup_field = "sample_id"


class MultipleSampleSerializer(serializers.ModelSerializer):
    """
    Serializer for adding multiple samples
    """

    class Meta:
        model = Sample
        fields = [
            "study_name",
            "sample_id",
            "sample_location",
            "sample_sublocation",
            "patient_id",
            "sample_type",
            "haemolysis_reference",
            "biopsy_location",
            "biopsy_inflamed_status",
            "sample_datetime",
            "processing_datetime",
            "frozen_datetime",
            "sample_comments",
            "sample_volume",
            "sample_volume_units",
            "freeze_thaw_count",
            "frozen_datetime",
        ]
        lookup_field = "sample_id"


class SampleExportSerializer(serializers.ModelSerializer):
    """
    Serializer for API data export
    """

    class Meta:
        model = Sample
        fields = [
            "study_name",
            "sample_id",
            "patient_id",
            "sample_type",
            "sample_location",
            "sample_sublocation",
            "sample_datetime",
            "sample_comments",
            "processing_datetime",
            "frozen_datetime",
            "sample_volume",
            "sample_volume_units",
            "freeze_thaw_count",
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
