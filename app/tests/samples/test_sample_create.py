import pytest
from django.urls import reverse

from app.factories import SampleFactory
from app.models import Sample

pytestmark = pytest.mark.django_db


def test_add_sample_page(auto_login_user):
    client, _ = auto_login_user()
    path = reverse("sample_add")

    response = client.get(path)
    assert response.status_code == 200

    response = client.post(path)
    assert response.status_code == 200


def test_add_sample_post(auto_login_user):
    client, _ = auto_login_user()
    path = reverse("sample_add")
    form_data = {
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

    response = client.post(path, data=form_data)

    assert Sample.objects.get(pk=1).study_id.name == "PATIENT001"
    assert response.status_code == 302


def test_add_sample_page_authenticated(sample_client):
    client, _ = sample_client

    response = client.get(reverse("sample_add"))

    assert response.status_code == 200


def test_add_marvel_sample(sample_client):
    client, _ = sample_client
    form_data = {
        "study_name": "marvel",
        "music_timepoint": "",
        "marvel_timepoint": "baseline",
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

    client.post(reverse("sample_add"), data=form_data)
    created_sample = Sample.objects.get(sample_id="TEST001")

    assert created_sample.study_name == "marvel"
    assert created_sample.frozen_datetime is None


def test_add_non_marvel_sample(sample_client):
    client, _ = sample_client
    form_data = {
        "study_name": "music",
        "music_timepoint": "baseline",
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

    client.post(reverse("sample_add"), data=form_data)
    created_sample = Sample.objects.get(sample_id="TEST001")

    assert created_sample.study_name != "marvel"


def test_add_marvel_sample_with_frozen_datetime(sample_client):
    client, _ = sample_client
    form_data = {
        "study_name": "marvel",
        "marvel_timepoint": "12_weeks",
        "sample_id": "test001",
        "study_id": "patient001",
        "sample_location": "location001",
        "sample_type": "cfdna_plasma",
        "sample_datetime": "2020-01-01T13:20:30",
        "sample_comments": "",
        "processing_datetime": "2020-01-01T13:20:30",
        "frozen_datetime": "2020-01-01T16:20:00",
        "sample_sublocation": "",
        "sample_volume": "",
        "sample_volume_units": "",
        "freeze_thaw_count": 0,
        "haemolysis_reference": "",
        "biopsy_location": "",
        "biopsy_inflamed_status": "",
    }

    client.post(reverse("sample_add"), data=form_data)
    created_sample = Sample.objects.get(sample_id="TEST001")

    assert created_sample.frozen_datetime is not None


def test_add_sample_unique(sample_client):
    SampleFactory(sample_id="TEST001")
    client, _ = sample_client
    form_data = {
        "study_name": "marvel",
        "marvel_timepoint": "12_weeks",
        "sample_id": "test001",
        "study_id": "patient001",
        "sample_location": "location001",
        "sample_type": "cfdna_plasma",
        "sample_datetime": "2020-01-01T13:20:30",
        "sample_comments": "",
        "processing_datetime": "2020-01-01T13:20:30",
        "frozen_datetime": "2020-01-01T16:20:00",
        "sample_sublocation": "",
        "sample_volume": "",
        "sample_volume_units": "",
        "freeze_thaw_count": 0,
        "haemolysis_reference": "",
        "biopsy_location": "",
        "biopsy_inflamed_status": "",
    }

    response = client.post(reverse("sample_add"), data=form_data)

    assert response.context["form"].errors["sample_id"][0] == "Sample with this Sample id already exists."
    assert Sample.objects.get(sample_id="TEST001").study_id != "patient001"
