from typing import Any, Dict, Optional

from rest_framework import serializers

from app.models import Sample
from core.utils.history import historical_changes


class SampleV3Serializer(serializers.ModelSerializer):
    """
    Serializer for the v3 API returning essential sample details aligned with the Django template.
    """

    study_name_label = serializers.CharField(source="get_study_name_display", read_only=True)
    sample_type_label = serializers.CharField(source="get_sample_type_display", read_only=True)
    study_identifier = serializers.SerializerMethodField()
    timepoint_label = serializers.SerializerMethodField()
    study_group_label = serializers.SerializerMethodField()
    age = serializers.IntegerField(source="study_id.age", allow_null=True, read_only=True)
    sex_label = serializers.SerializerMethodField()
    study_center_label = serializers.SerializerMethodField()
    genotype_data_available = serializers.SerializerMethodField()
    crp = serializers.SerializerMethodField()
    calprotectin = serializers.SerializerMethodField()
    endoscopic_mucosal_healing_at_3_6_months = serializers.SerializerMethodField()
    endoscopic_mucosal_healing_at_12_months = serializers.SerializerMethodField()

    class Meta:
        model = Sample
        fields = [
            "id",
            "sample_id",
            "study_name",
            "study_name_label",
            "study_identifier",
            "sample_location",
            "sample_sublocation",
            "sample_type",
            "sample_type_label",
            "sample_datetime",
            "timepoint_label",
            "study_group_label",
            "age",
            "sex_label",
            "study_center_label",
            "crp",
            "calprotectin",
            "endoscopic_mucosal_healing_at_3_6_months",
            "endoscopic_mucosal_healing_at_12_months",
            "genotype_data_available",
            "sample_comments",
            "is_used",
        ]
        lookup_field = "sample_id"

    @staticmethod
    def _format_choice(choice_value):
        if choice_value in (None, ""):
            return None
        return choice_value

    def get_study_identifier(self, obj: Sample):
        if obj.study_id is None:
            return None
        return {
            "id": obj.study_id.pk,
            "name": str(obj.study_id),
        }

    def get_timepoint_label(self, obj: Sample):
        if obj.music_timepoint:
            return self._format_choice(obj.get_music_timepoint_display())
        if obj.marvel_timepoint:
            return self._format_choice(obj.get_marvel_timepoint_display())
        return None

    def get_study_group_label(self, obj: Sample):
        if obj.study_id and obj.study_id.study_group:
            return self._format_choice(obj.study_id.get_study_group_display())
        return None

    def get_sex_label(self, obj: Sample):
        if obj.study_id and obj.study_id.sex:
            return self._format_choice(obj.study_id.get_sex_display())
        return None

    def get_study_center_label(self, obj: Sample):
        if obj.study_id and obj.study_id.study_center:
            return self._format_choice(obj.study_id.get_study_center_display())
        return None

    def get_genotype_data_available(self, obj: Sample):
        if obj.study_id is None:
            return None
        return obj.study_id.genotype_data_available

    def _numeric_or_none(self, value):
        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    def get_crp(self, obj: Sample):
        return self._numeric_or_none(getattr(obj, "crp", None))

    def get_calprotectin(self, obj: Sample):
        return self._numeric_or_none(getattr(obj, "calprotectin", None))

    def get_endoscopic_mucosal_healing_at_3_6_months(self, obj: Sample):
        value = getattr(obj, "endoscopic_mucosal_healing_at_3_6_months", None)
        if value is None:
            return None
        return bool(value)

    def get_endoscopic_mucosal_healing_at_12_months(self, obj: Sample):
        value = getattr(obj, "endoscopic_mucosal_healing_at_12_months", None)
        if value is None:
            return None
        return bool(value)


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

    def get_marvel_timepoint_label(self, obj: Sample) -> Optional[str]:
        return self._format_choice_display(obj.get_marvel_timepoint_display())

    def get_sample_volume_units_label(self, obj: Sample) -> Optional[str]:
        return self._format_choice_display(obj.get_sample_volume_units_display())

    def get_haemolysis_reference_label(self, obj: Sample) -> Optional[str]:
        return self._format_choice_display(obj.get_haemolysis_reference_display())

    def get_biopsy_location_label(self, obj: Sample) -> Optional[str]:
        return self._format_choice_display(obj.get_biopsy_location_display())

    def get_biopsy_inflamed_status_label(self, obj: Sample) -> Optional[str]:
        return self._format_choice_display(obj.get_biopsy_inflamed_status_display())

    def get_study_identifier(self, obj: Sample):
        if obj.study_id is None:
            return None
        return {
            "id": obj.study_id.pk,
            "name": str(obj.study_id),
        }

    def get_processing_time_minutes(self, obj: Sample) -> Optional[int]:
        if obj.processing_datetime is None or obj.sample_datetime is None:
            return None
        time_delta = obj.processing_datetime - obj.sample_datetime
        return int(time_delta.total_seconds() / 60)

    def get_history(self, obj: Sample) -> Dict[str, Any]:
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
