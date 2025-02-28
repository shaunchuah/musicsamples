import pytest
from django.utils import timezone

from app.views.datastore_api_views import FileDirectUploadFinishApi, FileDirectUploadStartApi


class TestFileDirectUploadStartApiSerializer:
    @pytest.fixture
    def valid_data(self):
        return {
            "category": "sample_category",
            "study_name": "test_study",
            "study_id": "123",
            "music_timepoint": "timepoint1",
            "marvel_timepoint": "timepoint2",
            "sampling_date": timezone.now().date(),
            "comments": "test comment",
            "file_name": "test_file.wav",
        }

    def test_valid_data(self, valid_data):
        serializer = FileDirectUploadStartApi.InputSerializer(data=valid_data)
        assert serializer.is_valid()
        assert serializer.validated_data["category"] == valid_data["category"]
        assert serializer.validated_data["study_name"] == valid_data["study_name"]
        assert serializer.validated_data["file_name"] == valid_data["file_name"]

    def test_minimal_valid_data(self):
        # Only required fields
        minimal_data = {"category": "sample_category", "study_name": "test_study", "file_name": "test_file.wav"}
        serializer = FileDirectUploadStartApi.InputSerializer(data=minimal_data)
        assert serializer.is_valid()

    def test_missing_required_fields(self):
        # Missing category
        data = {"study_name": "test_study", "file_name": "test_file.wav"}
        serializer = FileDirectUploadStartApi.InputSerializer(data=data)
        assert not serializer.is_valid()
        assert "category" in serializer.errors

        # Missing study_name
        data = {"category": "sample_category", "file_name": "test_file.wav"}
        serializer = FileDirectUploadStartApi.InputSerializer(data=data)
        assert not serializer.is_valid()
        assert "study_name" in serializer.errors

        # Missing file_name
        data = {"category": "sample_category", "study_name": "test_study"}
        serializer = FileDirectUploadStartApi.InputSerializer(data=data)
        assert not serializer.is_valid()
        assert "file_name" in serializer.errors

    def test_validate_study_id(self):
        # Test empty string becomes None
        data = {
            "category": "sample_category",
            "study_name": "test_study",
            "study_id": "",
            "file_name": "test_file.wav",
        }
        serializer = FileDirectUploadStartApi.InputSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data["study_id"] is None

        # Test non-empty string stays as is
        data["study_id"] = "123"
        serializer = FileDirectUploadStartApi.InputSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data["study_id"] == "123"

    def test_invalid_date_format(self, valid_data):
        valid_data["sampling_date"] = "not-a-date"
        serializer = FileDirectUploadStartApi.InputSerializer(data=valid_data)
        assert not serializer.is_valid()
        assert "sampling_date" in serializer.errors


class TestFileDirectUploadFinishApiSerializer:
    def test_valid_data(self):
        data = {"file_id": "abc123"}
        serializer = FileDirectUploadFinishApi.InputSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data["file_id"] == "abc123"

    def test_missing_file_id(self):
        data = {}
        serializer = FileDirectUploadFinishApi.InputSerializer(data=data)
        assert not serializer.is_valid()
        assert "file_id" in serializer.errors
