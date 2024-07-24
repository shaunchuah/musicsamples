import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient, APITestCase

pytestmark = pytest.mark.django_db

User = get_user_model()


class MultipleSamplesTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(username="testowy", password="test")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_invalid_response_without_study_name(self):
        sample_data = {
            "study_name": "",
            "sample_id": "test001",
            "patient_id": "patient001",
            "sample_location": "location001",
            "sample_type": "test_sample_type",
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
        response = self.client.post(
            "/api/multiple_samples/", sample_data, format="json"
        )
        print(response.data)
        assert response.status_code == 400  # bad request
        assert response.data["study_name"][0].code == "invalid_choice"

    def test_patient_id_uppercase(self):
        sample_data = {
            "study_name": "gidamps",
            "sample_id": "test001",
            "patient_id": "patient001",
            "sample_location": "location001",
            "sample_type": "test_sample_type",
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
        response = self.client.post(
            "/api/multiple_samples/", sample_data, format="json"
        )
        assert response.status_code == 201
        assert response.data["patient_id"] == "PATIENT001"
