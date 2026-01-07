# api_v3/tests/test_study_ids.py
# Exercises the study identifier detail/update endpoints consumed by the Next.js study ID modals.
# Exists to lock in the history payload and uppercase update behavior the frontend relies on.

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from app.factories import StudyIdentifierFactory
from users.factories import UserFactory

pytestmark = pytest.mark.django_db


def test_study_id_detail_includes_history_entries():
    user = UserFactory()
    client = APIClient()
    client.force_authenticate(user=user)

    study = StudyIdentifierFactory()
    study.study_group = "uc"
    study.save()
    study.study_group = "cd"
    study.save()

    url = reverse("v3-study-ids-detail", args=[study.id])
    response = client.get(url, format="json")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == study.id
    assert isinstance(body.get("history"), list)
    assert any(
        change.get("field") == "study_group" for entry in body["history"] for change in entry.get("changes", [])
    )


def test_study_id_patch_uppercases_name_and_preserves_choices():
    user = UserFactory()
    client = APIClient()
    client.force_authenticate(user=user)

    study = StudyIdentifierFactory(name="Demo-Lowercase", study_name="gidamps")

    url = reverse("v3-study-ids-detail", args=[study.id])
    response = client.patch(
        url,
        {"name": "demo-lowercase", "study_name": "music"},
        format="json",
    )

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "DEMO-LOWERCASE"
    assert body["study_name"] == "music"

    study.refresh_from_db()
    assert study.name == "DEMO-LOWERCASE"
    assert study.study_name == "music"
