import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient, APITestCase

from app.models import Sample

pytestmark = pytest.mark.django_db

User = get_user_model()


class MultipleSamplesTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(email="test@test.com", password="test")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_invalid_response_without_study_name(self):
        sample_data = {
            "study_name": "",
            "sample_id": "test001",
            "study_id": "patient001",
            "sample_location": "location001",
            "sample_type": "cfdna_plasma",
            "sample_datetime": "2020-01-01T13:20:30",
            "sample_comments": "",
            "processing_datetime": "2020-01-01T13:20:30",
            "sample_sublocation": "",
            "sample_volume": "",
            "sample_volume_units": "",
            "freeze_thaw_count": 0,
            "haemolysis_reference": "",
            "biopsy_location": "",
            "biopsy_inflamed_status": "",
        }
        response = self.client.post("/api/multiple_samples/", sample_data, format="json")
        assert response.status_code == 400  # bad request
        assert response.data["study_name"][0].code == "invalid_choice"

    def test_study_id_uppercase(self):
        sample_data = {
            "study_name": "gidamps",
            "sample_id": "test001",
            "study_id": "patient001",
            "sample_location": "location001",
            "sample_type": "cfdna_plasma",
            "sample_datetime": "2020-01-01T13:20:30",
            "sample_comments": "",
            "processing_datetime": "2020-01-01T13:20:30",
            "sample_sublocation": "",
            "sample_volume": "",
            "sample_volume_units": "",
            "freeze_thaw_count": 0,
            "haemolysis_reference": "",
            "biopsy_location": "",
            "biopsy_inflamed_status": "",
        }
        response = self.client.post("/api/multiple_samples/", sample_data, format="json")
        assert response.status_code == 201
        assert response.data["study_id"] == "PATIENT001"

    def test_music_sample_without_timepoint(self):
        sample_data = {
            "study_name": "music",
            "music_timepoint": "",
            "marvel_timepoint": "",
            "sample_id": "test001",
            "study_id": "patient001",
            "sample_location": "location001",
            "sample_type": "cfdna_plasma",
            "sample_datetime": "2020-01-01T13:20:30",
            "sample_comments": "",
            "processing_datetime": "2020-01-01T13:20:30",
            "sample_sublocation": "",
            "sample_volume": "",
            "sample_volume_units": "",
            "freeze_thaw_count": 0,
            "haemolysis_reference": "",
            "biopsy_location": "",
            "biopsy_inflamed_status": "",
        }
        response = self.client.post("/api/multiple_samples/", sample_data, format="json")
        assert response.status_code == 400  # bad request
        assert response.data["non_field_errors"][0].code == "invalid"

    def test_mini_music_sample_without_timepoint(self):
        sample_data = {
            "study_name": "mini_music",
            "music_timepoint": "",
            "marvel_timepoint": "",
            "sample_id": "test001",
            "study_id": "patient001",
            "sample_location": "location001",
            "sample_type": "cfdna_plasma",
            "sample_datetime": "2020-01-01T13:20:30",
            "sample_comments": "",
            "processing_datetime": "2020-01-01T13:20:30",
            "sample_sublocation": "",
            "sample_volume": "",
            "sample_volume_units": "",
            "freeze_thaw_count": 0,
            "haemolysis_reference": "",
            "biopsy_location": "",
            "biopsy_inflamed_status": "",
        }
        response = self.client.post("/api/multiple_samples/", sample_data, format="json")
        assert response.status_code == 400  # bad request
        assert response.data["non_field_errors"][0].code == "invalid"

    def test_marvel_sample_without_timepoint(self):
        sample_data = {
            "study_name": "marvel",
            "music_timepoint": "",
            "marvel_timepoint": "",
            "sample_id": "test001",
            "study_id": "patient001",
            "sample_location": "location001",
            "sample_type": "cfdna_plasma",
            "sample_datetime": "2020-01-01T13:20:30",
            "sample_comments": "",
            "processing_datetime": "2020-01-01T13:20:30",
            "sample_sublocation": "",
            "sample_volume": "",
            "sample_volume_units": "",
            "freeze_thaw_count": 0,
            "haemolysis_reference": "",
            "biopsy_location": "",
            "biopsy_inflamed_status": "",
        }
        response = self.client.post("/api/multiple_samples/", sample_data, format="json")
        assert response.status_code == 400  # bad request
        assert response.data["non_field_errors"][0].code == "invalid"

    def test_sample_id_saved_as_uppercase(self):
        """Test that sample_id is converted to uppercase when creating a sample."""
        sample_data = {
            "study_name": "gidamps",
            "sample_id": "test001lowercase",
            "study_id": "patient001",
            "sample_location": "location001",
            "sample_type": "cfdna_plasma",
            "sample_datetime": "2020-01-01T13:20:30",
            "processing_datetime": "2020-01-01T13:20:30",
            "sample_comments": "",
            "sample_sublocation": "",
            "sample_volume": "",
            "sample_volume_units": "",
            "freeze_thaw_count": 0,
            "haemolysis_reference": "",
            "biopsy_location": "",
            "biopsy_inflamed_status": "",
        }

        response = self.client.post("/api/multiple_samples/", sample_data, format="json")
        assert response.status_code == 201  # created successfully
        assert response.data["sample_id"] == "TEST001LOWERCASE"  # check that the ID was converted to uppercase

        # Verify the same record in the database is also uppercase
        saved_sample = Sample.objects.get(sample_id="TEST001LOWERCASE")
        assert saved_sample.sample_id == "TEST001LOWERCASE"
