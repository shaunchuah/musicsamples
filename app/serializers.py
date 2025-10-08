from rest_framework import serializers

from app.models import Sample, StudyIdentifier
from core.utils.history import historical_changes


class SampleLocationSerializer(serializers.ModelSerializer):
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


class SampleV2Serializer(serializers.ModelSerializer):
    """
    Serializer for NextJS Fronend
    """

    class Meta:
        model = Sample
        fields = "__all__"
        lookup_field = "sample_id"


class SampleV3Serializer(serializers.ModelSerializer):
    """
    Serializer for the v3 API returning essential sample details.
    """

    class Meta:
        model = Sample
        fields = [
            "sample_id",
            "study_name",
            "sample_type",
            "sample_datetime",
            "sample_location",
            "sample_sublocation",
            "is_used",
        ]
        lookup_field = "sample_id"


class SampleHistoryChangeSerializer(serializers.Serializer):
    """
    Serializes individual field-level history changes for audit panels.
    """

    field = serializers.CharField()
    label = serializers.CharField()
    old = serializers.CharField(allow_null=True, required=False)
    new = serializers.CharField(allow_null=True, required=False)


class SampleHistoryEntrySerializer(serializers.Serializer):
    """
    Serializes timeline entries combining timestamp, user and detailed changes.
    """

    timestamp = serializers.DateTimeField()
    user = serializers.CharField(allow_null=True)
    summary = serializers.CharField(allow_null=True, required=False)
    changes = SampleHistoryChangeSerializer(many=True)


class SampleHistorySerializer(serializers.Serializer):
    """
    Wraps history metadata alongside the chronological entries list.
    """

    created = serializers.DateTimeField()
    created_by = serializers.CharField(allow_null=True)
    last_modified = serializers.DateTimeField()
    last_modified_by = serializers.CharField(allow_null=True)
    entries = SampleHistoryEntrySerializer(many=True)


class SampleV3DetailSerializer(serializers.ModelSerializer):
    """
    Expanded serializer for sample detail view including processing metadata and history.
    """

    study_name_label = serializers.CharField(source="get_study_name_display", read_only=True)
    sample_type_label = serializers.CharField(source="get_sample_type_display", read_only=True)
    music_timepoint_label = serializers.SerializerMethodField()
    marvel_timepoint_label = serializers.SerializerMethodField()
    sample_volume_units_label = serializers.SerializerMethodField()
    haemolysis_reference_label = serializers.SerializerMethodField()
    biopsy_location_label = serializers.SerializerMethodField()
    biopsy_inflamed_status_label = serializers.SerializerMethodField()
    study_identifier = serializers.SerializerMethodField()
    processing_time_minutes = serializers.SerializerMethodField()
    history = serializers.SerializerMethodField()

    class Meta:
        model = Sample
        fields = [
            "sample_id",
            "study_name",
            "study_name_label",
            "study_identifier",
            "music_timepoint",
            "music_timepoint_label",
            "marvel_timepoint",
            "marvel_timepoint_label",
            "sample_type",
            "sample_type_label",
            "sample_datetime",
            "sample_location",
            "sample_sublocation",
            "sample_comments",
            "is_used",
            "processing_datetime",
            "processing_time_minutes",
            "frozen_datetime",
            "sample_volume",
            "sample_volume_units",
            "sample_volume_units_label",
            "freeze_thaw_count",
            "haemolysis_reference",
            "haemolysis_reference_label",
            "biopsy_location",
            "biopsy_location_label",
            "biopsy_inflamed_status",
            "biopsy_inflamed_status_label",
            "qubit_cfdna_ng_ul",
            "paraffin_block_key",
            "created",
            "created_by",
            "last_modified",
            "last_modified_by",
            "history",
        ]
        lookup_field = "sample_id"

    @staticmethod
    def _format_choice_display(display_value):
        return display_value if display_value not in (None, "") else None

    @staticmethod
    def _format_history_user(user):
        if user is None:
            return None
        email = getattr(user, "email", None)
        if isinstance(email, str) and email:
            return email
        username = getattr(user, "username", None)
        if isinstance(username, str) and username:
            return username
        return str(user)

    @staticmethod
    def _format_field_label(field_name: str) -> str:
        return field_name.replace("_", " ").title()

    def get_music_timepoint_label(self, obj: Sample):
        return self._format_choice_display(obj.get_music_timepoint_display())

    def get_marvel_timepoint_label(self, obj: Sample):
        return self._format_choice_display(obj.get_marvel_timepoint_display())

    def get_sample_volume_units_label(self, obj: Sample):
        return self._format_choice_display(obj.get_sample_volume_units_display())

    def get_haemolysis_reference_label(self, obj: Sample):
        return self._format_choice_display(obj.get_haemolysis_reference_display())

    def get_biopsy_location_label(self, obj: Sample):
        return self._format_choice_display(obj.get_biopsy_location_display())

    def get_biopsy_inflamed_status_label(self, obj: Sample):
        return self._format_choice_display(obj.get_biopsy_inflamed_status_display())

    def get_study_identifier(self, obj: Sample):
        if obj.study_id is None:
            return None
        return {
            "id": obj.study_id.pk,
            "name": str(obj.study_id),
        }

    def get_processing_time_minutes(self, obj: Sample):
        if obj.processing_datetime is None or obj.sample_datetime is None:
            return None
        time_delta = obj.processing_datetime - obj.sample_datetime
        return int(time_delta.total_seconds() / 60)

    def get_history(self, obj: Sample):
        history_qs = obj.history.all()
        changes = historical_changes(history_qs) or []

        entries = []
        for delta in changes:
            new_record = delta.new_record
            resolved_user = self._format_history_user(getattr(new_record, "history_user", None))
            entry_changes = []
            for change in delta.changes:
                entry_changes.append(
                    {
                        "field": change.field,
                        "label": self._format_field_label(change.field),
                        "old": change.old if change.old not in ("", None) else None,
                        "new": change.new if change.new not in ("", None) else None,
                    }
                )
            entries.append(
                {
                    "timestamp": getattr(new_record, "history_date", obj.last_modified),
                    "user": resolved_user,
                    "summary": None,
                    "changes": entry_changes,
                }
            )

        entries.append(
            {
                "timestamp": obj.created,
                "user": obj.created_by,
                "summary": "Record created",
                "changes": [],
            }
        )

        history_payload = {
            "created": obj.created,
            "created_by": obj.created_by,
            "last_modified": obj.last_modified,
            "last_modified_by": obj.last_modified_by,
            "entries": entries,
        }

        serializer = SampleHistorySerializer(history_payload)
        return serializer.data


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

    study_id = serializers.CharField()

    class Meta:
        model = Sample
        fields = [
            "study_name",
            "music_timepoint",
            "marvel_timepoint",
            "sample_id",
            "sample_location",
            "sample_sublocation",
            "study_id",
            "sample_type",
            "qubit_cfdna_ng_ul",
            "haemolysis_reference",
            "paraffin_block_key",
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

    def validate(self, data):
        """
        Check that music_timepoint is not empty if study_name is music or mini_music
        """

        if data["study_name"] == "music" or data["study_name"] == "mini_music":
            if not data["music_timepoint"]:
                raise serializers.ValidationError("Music Timepoint must be filled for MUSIC and Mini-MUSIC studies.")

        if data["study_name"] == "marvel":
            if not data["marvel_timepoint"]:
                raise serializers.ValidationError(
                    "Marvel Timepoint must be filled for MARVEL and Mini-MARVEL studies."
                )

        return data

    def create(self, validated_data):
        study_id = validated_data.pop("study_id", None)

        if study_id:
            study_id = study_id.upper()
            study_identifier, _ = StudyIdentifier.objects.get_or_create(name=study_id)
            validated_data["study_id"] = study_identifier

        return super().create(validated_data)


class SampleExportSerializer(serializers.ModelSerializer):
    """
    Serializer for API data export
    """

    class Meta:
        model = Sample
        fields = [
            "study_name",
            "sample_id",
            "study_id",
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
