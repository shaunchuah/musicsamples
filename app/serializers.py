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


class SampleIsUsedSerializer(serializers.ModelSerializer):
    """
    Serializer for marking samples as used
    """

    class Meta:
        model = Sample
        fields = [
            "sample_id",
            "is_used",
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
            "music_timepoint",
            "marvel_timepoint",
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

    def create(self, validated_data):
        validated_data["patient_id"] = validated_data["patient_id"].upper()
        return super(MultipleSampleSerializer, self).create(validated_data)

    def validate(self, data):
        """
        Check that music_timepoint is not empty if study_name is music or mini_music
        """

        if data["study_name"] == "music" or data["study_name"] == "mini_music":
            if not data["music_timepoint"]:
                raise serializers.ValidationError(
                    "Music Timepoint must be filled for MUSIC and Mini-MUSIC studies."
                )

        if data["study_name"] == "marvel" or data["study_name"] == "mini_marvel":
            if not data["marvel_timepoint"]:
                raise serializers.ValidationError(
                    "Marvel Timepoint must be filled for MARVEL and Mini-MARVEL studies."
                )

        return data


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
            "is_used",
            "haemolysis_reference",
            "biopsy_location",
            "biopsy_inflamed_status",
            "created_by",
            "last_modified_by",
            "created",
            "last_modified",
        ]
        lookup_field = "sample_id"
