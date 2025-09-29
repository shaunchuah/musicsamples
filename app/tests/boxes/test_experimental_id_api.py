import pytest
from django.urls import reverse

from app.choices import BasicScienceGroupChoices, SpeciesChoices
from app.factories import BasicScienceSampleTypeFactory, TissueTypeFactory
from app.models import ExperimentalID

pytestmark = pytest.mark.django_db


def test_create_experimental_id_requires_login(client):
    response = client.post(reverse("boxes:create_experimental_id"), {})

    assert response.status_code == 302
    assert "/login/" in response["Location"]


def test_create_experimental_id_requires_permission(client, box_user):
    client.force_login(box_user)

    response = client.post(reverse("boxes:create_experimental_id"), {})

    assert response.status_code == 403


def test_create_experimental_id_success_returns_serialized_payload(client, box_user, grant_permission):
    client.force_login(box_user)
    grant_permission(box_user, "view_basicsciencebox")
    grant_permission(box_user, "add_experimentalid")

    sample_type = BasicScienceSampleTypeFactory()
    tissue_type = TissueTypeFactory()

    payload = {
        "basic_science_group": BasicScienceGroupChoices.BAIN.value,
        "name": "EXP-TEST-001",
        "description": "Test experiment",
        "date": "2024-01-01",
        "sample_types": [sample_type.pk],
        "tissue_types": [tissue_type.pk],
        "species": SpeciesChoices.HUMAN.value,
    }

    response = client.post(reverse("boxes:create_experimental_id"), payload)

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    experimental_id = data["experimental_id"]
    assert experimental_id["name"] == payload["name"]
    assert experimental_id["basic_science_group"] == payload["basic_science_group"]
    assert sample_type.pk in experimental_id["sample_type_ids"]
    assert experimental_id["created_by"] == box_user.email

    saved_experiment = ExperimentalID.objects.get(name=payload["name"])
    assert saved_experiment.created_by == box_user
    assert saved_experiment.sample_types.filter(pk=sample_type.pk).exists()
    assert saved_experiment.tissue_types.filter(pk=tissue_type.pk).exists()


def test_create_experimental_id_invalid_returns_errors(client, box_user, grant_permission):
    client.force_login(box_user)
    grant_permission(box_user, "view_basicsciencebox")

    initial_count = ExperimentalID.objects.count()

    response = client.post(
        reverse("boxes:create_experimental_id"),
        {"basic_science_group": BasicScienceGroupChoices.BAIN.value, "species": SpeciesChoices.HUMAN.value},
    )

    assert response.status_code == 400
    data = response.json()
    assert data["success"] is False
    assert "errors" in data
    assert "name" in data["errors"]
    assert ExperimentalID.objects.count() == initial_count
