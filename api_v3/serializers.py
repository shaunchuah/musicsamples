from typing import Any, Dict, Optional

from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from app.models import BasicScienceBox, Experiment, Sample, StudyIdentifier
from core.utils.history import historical_changes


class ExperimentBoxSummarySerializer(serializers.ModelSerializer):
    """
    Minimal box summary for experiment listings.
    """

    class Meta:
        model = BasicScienceBox
        fields = ["id", "box_id"]


class ExperimentV3Serializer(serializers.ModelSerializer):
    """
    Serializer for the v3 API returning experiment details aligned with the Django template.
    """

    basic_science_group_label = serializers.CharField(
        source="get_basic_science_group_display",
        read_only=True,
    )
    species_label = serializers.CharField(source="get_species_display", read_only=True)
    sample_type_labels = serializers.SerializerMethodField()
    tissue_type_labels = serializers.SerializerMethodField()
    boxes = serializers.SerializerMethodField()
    created_by_email = serializers.SerializerMethodField()

    class Meta:
        model = Experiment
        fields = [
            "id",
            "date",
            "basic_science_group",
            "basic_science_group_label",
            "name",
            "description",
            "sample_type_labels",
            "tissue_type_labels",
            "species",
            "species_label",
            "boxes",
            "created",
            "created_by_email",
            "is_deleted",
        ]

    def get_sample_type_labels(self, obj: Experiment):
        return [sample_type.label or sample_type.name for sample_type in obj.sample_types.all()]

    def get_tissue_type_labels(self, obj: Experiment):
        return [tissue_type.label or tissue_type.name for tissue_type in obj.tissue_types.all()]

    def get_boxes(self, obj: Experiment):
        return ExperimentBoxSummarySerializer(obj.boxes.all(), many=True).data

    def get_created_by_email(self, obj: Experiment):
        user = getattr(obj, "created_by", None)
        if user is None:
            return None
        email = getattr(user, "email", None)
        if isinstance(email, str) and email:
            return email
        username = getattr(user, "username", None)
        if isinstance(username, str) and username:
            return username
        return str(user)


class BasicScienceBoxExperimentSerializer(serializers.ModelSerializer):
    """
    Minimal experiment summary for box listings.
    """

    class Meta:
        model = Experiment
        fields = ["id", "name", "date"]


class BasicScienceBoxCreateV3Serializer(serializers.ModelSerializer):
    """
    Serializer for creating basic science boxes from the v3 API.
    """

    box_id = serializers.CharField(validators=[UniqueValidator(queryset=BasicScienceBox.objects.all())])
    experiments = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Experiment.objects.all(),
        required=False,
    )

    class Meta:
        model = BasicScienceBox
        fields = [
            "box_id",
            "basic_science_group",
            "box_type",
            "location",
            "row",
            "column",
            "depth",
            "comments",
            "experiments",
        ]


class BasicScienceBoxUpdateV3Serializer(serializers.ModelSerializer):
    """
    Serializer for updating basic science boxes from the v3 API.
    """

    box_id = serializers.CharField(validators=[UniqueValidator(queryset=BasicScienceBox.objects.all())])
    experiments = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Experiment.objects.all(),
        required=False,
    )

    class Meta:
        model = BasicScienceBox
        fields = [
            "box_id",
            "basic_science_group",
            "box_type",
            "location",
            "row",
            "column",
            "depth",
            "comments",
            "experiments",
            "is_used",
        ]


class BasicScienceBoxV3Serializer(serializers.ModelSerializer):
    """
    Serializer for the v3 API returning box details aligned with the Django template.
    """

    basic_science_groups_display = serializers.CharField(read_only=True)
    basic_science_group_label = serializers.CharField(
        source="get_basic_science_group_display",
        read_only=True,
    )
    species_display = serializers.CharField(read_only=True)
    location_label = serializers.CharField(source="get_location_display", read_only=True)
    box_type_label = serializers.CharField(source="get_box_type_display", read_only=True)
    sample_type_labels = serializers.SerializerMethodField()
    tissue_type_labels = serializers.SerializerMethodField()
    experiments = serializers.SerializerMethodField()
    created_by_email = serializers.SerializerMethodField()
    sublocation = serializers.SerializerMethodField()

    class Meta:
        model = BasicScienceBox
        fields = [
            "id",
            "box_id",
            "basic_science_group",
            "basic_science_group_label",
            "basic_science_groups_display",
            "experiments",
            "species_display",
            "location",
            "location_label",
            "row",
            "column",
            "depth",
            "sublocation",
            "box_type",
            "box_type_label",
            "sample_type_labels",
            "tissue_type_labels",
            "comments",
            "created",
            "created_by_email",
            "is_used",
        ]

    def get_sample_type_labels(self, obj: BasicScienceBox):
        return obj.get_sample_type_labels()

    def get_tissue_type_labels(self, obj: BasicScienceBox):
        return obj.get_tissue_type_labels()

    def get_experiments(self, obj: BasicScienceBox):
        return BasicScienceBoxExperimentSerializer(obj.experiments.all(), many=True).data

    def get_created_by_email(self, obj: BasicScienceBox):
        user = getattr(obj, "created_by", None)
        if user is None:
            return None
        email = getattr(user, "email", None)
        if isinstance(email, str) and email:
            return email
        username = getattr(user, "username", None)
        if isinstance(username, str) and username:
            return username
        return str(user)

    def get_sublocation(self, obj: BasicScienceBox):
        row = obj.row or ""
        column = obj.column or ""
        depth = obj.depth or ""
        combined = f"{row}{column}{depth}".strip()
        return combined or None


class BasicScienceBoxDetailV3Serializer(BasicScienceBoxV3Serializer):
    """
    Detail serializer for boxes, including audit history metadata.
    """

    last_modified = serializers.DateTimeField(read_only=True)
    last_modified_by_email = serializers.SerializerMethodField()
    history = serializers.SerializerMethodField()

    class Meta(BasicScienceBoxV3Serializer.Meta):
        fields = BasicScienceBoxV3Serializer.Meta.fields + [
            "last_modified",
            "last_modified_by_email",
            "history",
        ]

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

    def _resolve_history_user_value(self, value):
        if value in (None, ""):
            return None
        if hasattr(value, "email") or hasattr(value, "username"):
            return self._format_history_user(value)
        try:
            user_id = int(value)
        except (TypeError, ValueError):
            return str(value)
        user_cache = getattr(self, "_history_user_cache", None)
        if user_cache is None:
            user_cache = {}
            setattr(self, "_history_user_cache", user_cache)
        if user_id in user_cache:
            return user_cache[user_id]
        User = get_user_model()
        user = User.objects.filter(pk=user_id).first()
        resolved = self._format_history_user(user) if user else str(value)
        user_cache[user_id] = resolved
        return resolved

    def get_last_modified_by_email(self, obj: BasicScienceBox):
        return self._format_history_user(getattr(obj, "last_modified_by", None))

    def get_history(self, obj: BasicScienceBox) -> Dict[str, Any]:
        history_qs = obj.history.all()
        changes = historical_changes(history_qs) or []

        entries = []
        for delta in changes:
            new_record = delta.new_record
            resolved_user = self._format_history_user(getattr(new_record, "history_user", None))
            entry_changes = []
            for change in delta.changes:
                change_old = change.old
                change_new = change.new
                if change.field in ("created_by", "last_modified_by"):
                    change_old = self._resolve_history_user_value(change.old)
                    change_new = self._resolve_history_user_value(change.new)
                entry_changes.append(
                    {
                        "field": change.field,
                        "label": self._format_field_label(change.field),
                        "old": change_old if change_old not in ("", None) else None,
                        "new": change_new if change_new not in ("", None) else None,
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
            "created_by": self._format_history_user(obj.created_by),
            "last_modified": obj.last_modified,
            "last_modified_by": self._format_history_user(obj.last_modified_by),
            "entries": entries,
        }

        serializer = SampleHistorySerializer(history_payload)
        return serializer.data


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


class SampleV3UpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating existing samples from the v3 dashboard.
    """

    study_id = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    frozen_datetime = serializers.DateTimeField(required=False, allow_null=True)
    processing_datetime = serializers.DateTimeField(required=False, allow_null=True)
    sample_datetime = serializers.DateTimeField(required=False, allow_null=True)

    class Meta:
        model = Sample
        fields = [
            "study_name",
            "music_timepoint",
            "marvel_timepoint",
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
        ]
        lookup_field = "sample_id"

    def validate(self, data):
        if not any(field in data for field in ("study_name", "music_timepoint", "marvel_timepoint")):
            return data

        study_name = data.get("study_name") or getattr(self.instance, "study_name", None)
        music_timepoint = data.get("music_timepoint", getattr(self.instance, "music_timepoint", None))
        marvel_timepoint = data.get("marvel_timepoint", getattr(self.instance, "marvel_timepoint", None))

        if study_name in ("music", "mini_music") and not music_timepoint:
            raise serializers.ValidationError("Music Timepoint must be filled for MUSIC and Mini-MUSIC studies.")

        if study_name == "marvel" and not marvel_timepoint:
            raise serializers.ValidationError("Marvel Timepoint must be filled for MARVEL studies.")

        return data

    def update(self, instance, validated_data):
        study_id = validated_data.pop("study_id", None)
        if study_id is not None:
            if study_id in ("", None):
                instance.study_id = None
            else:
                study_identifier, _ = StudyIdentifier.objects.get_or_create(name=str(study_id).upper())
                instance.study_id = study_identifier

        return super().update(instance, validated_data)


class MultipleSampleV3Serializer(serializers.ModelSerializer):
    """
    Serializer for adding multiple samples via the v3 QR scan workflow.
    """

    study_id = serializers.CharField()
    frozen_datetime = serializers.DateTimeField(required=False, allow_null=True)
    processing_datetime = serializers.DateTimeField(required=False, allow_null=True)
    sample_id = serializers.CharField(validators=[UniqueValidator(queryset=Sample.objects.all(), lookup="iexact")])

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
        ]
        lookup_field = "sample_id"

    def validate(self, data):
        if data["study_name"] in ("music", "mini_music") and not data.get("music_timepoint"):
            raise serializers.ValidationError("Music Timepoint must be filled for MUSIC and Mini-MUSIC studies.")

        if data["study_name"] == "marvel" and not data.get("marvel_timepoint"):
            raise serializers.ValidationError("Marvel Timepoint must be filled for MARVEL studies.")

        return data

    def validate_sample_id(self, value):
        return value.upper()

    def create(self, validated_data):
        study_id = validated_data.pop("study_id", None)

        if study_id:
            study_identifier, _ = StudyIdentifier.objects.get_or_create(name=study_id.upper())
            validated_data["study_id"] = study_identifier

        return super().create(validated_data)


class SampleLocationV3Serializer(serializers.ModelSerializer):
    """
    Serializer for updating sample locations via QR scan workflows.
    """

    class Meta:
        model = Sample
        fields = [
            "sample_id",
            "sample_location",
            "sample_sublocation",
        ]
        lookup_field = "sample_id"


class SampleIsUsedV3Serializer(serializers.ModelSerializer):
    """
    Serializer for marking samples as used via QR scan workflows.
    """

    class Meta:
        model = Sample
        fields = [
            "sample_id",
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
