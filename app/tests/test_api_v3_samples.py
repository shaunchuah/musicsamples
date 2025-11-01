# app/tests/test_api_v3_samples.py
# Tests the SampleV3 API endpoints to ensure audit metadata is stamped correctly.
# Exists to prevent regressions where created_by or last_modified_by lose the authenticated user.

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from app.choices import SampleTypeChoices, StudyNameChoices
from app.factories import SampleFactory
from app.models import Sample
from users.factories import UserFactory

pytestmark = pytest.mark.django_db


def _authenticated_client():
    """
    Returns an API client authenticated as a user with a known email.
    """
    user = UserFactory(email="api-user@example.com")
    client = APIClient()
    client.force_authenticate(user=user)
    return client, user


def test_sample_create_stamps_audit_fields():
    client, user = _authenticated_client()
    payload = {
        "study_name": StudyNameChoices.MUSIC,
        "sample_id": "API-00001",
        "sample_location": "Test Location",
        "sample_type": SampleTypeChoices.CFDNA_PLASMA,
        "sample_datetime": "2024-01-01T12:00:00Z",
        "sample_comments": "Created via API",
        "is_used": False,
    }

    response = client.post(reverse("v3-samples-list"), payload, format="json")

    assert response.status_code == 201
    created = Sample.objects.get(sample_id=payload["sample_id"])
    assert created.created_by == user.email
    assert created.last_modified_by == user.email


def test_sample_update_refreshes_last_modified_by():
    sample = SampleFactory(
        sample_id="API-00002",
        created_by="creator@example.com",
        last_modified_by="previous-editor@example.com",
    )
    client, user = _authenticated_client()
    url = reverse("v3-samples-detail", kwargs={"sample_id": sample.sample_id})

    response = client.patch(url, {"sample_comments": "Updated via API"}, format="json")

    assert response.status_code == 200
    sample.refresh_from_db()
    assert sample.created_by == "creator@example.com"
    assert sample.last_modified_by == user.email
