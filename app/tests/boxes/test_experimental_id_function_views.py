import pytest
from django.urls import reverse

from app.factories import ExperimentalIDFactory

pytestmark = pytest.mark.django_db


def test_experimental_id_search_requires_login(client):
    response = client.get(reverse("boxes:experimental_id_search"), {"q": "Search"})

    assert response.status_code == 302


def test_experimental_id_search_returns_matches(client, box_user, grant_permission):
    match = ExperimentalIDFactory(name="Search Target", description="Interesting experiment")
    ExperimentalIDFactory(name="Background", description="Other")
    client.force_login(box_user)
    grant_permission(box_user, "view_basicsciencebox")

    response = client.get(reverse("boxes:experimental_id_search"), {"q": "Search"})

    assert response.status_code == 200
    assert match in response.context["experimental_ids"]


def test_export_experimental_ids_csv(client, box_user, grant_permission):
    experiment = ExperimentalIDFactory(name="CSV Target")
    client.force_login(box_user)
    grant_permission(box_user, "view_basicsciencebox")

    response = client.get(reverse("boxes:experimental_id_export_csv"), {"q": experiment.name})

    assert response.status_code == 200
    assert response["Content-Type"] == "text/csv"


def test_experimental_id_filter_requires_permission(client, box_user):
    client.force_login(box_user)

    response = client.get(reverse("boxes:experimental_id_filter"))

    assert response.status_code == 403


def test_experimental_id_filter_returns_context(client, box_user, grant_permission):
    client.force_login(box_user)
    grant_permission(box_user, "view_basicsciencebox")

    response = client.get(reverse("boxes:experimental_id_filter"))

    assert response.status_code == 200
    assert "experimental_id_filter" in response.context


def test_experimental_id_filter_export_csv(client, box_user, grant_permission):
    client.force_login(box_user)
    grant_permission(box_user, "view_basicsciencebox")

    response = client.get(reverse("boxes:experimental_id_filter_export_csv"))

    assert response.status_code == 200
    assert response["Content-Type"] == "text/csv"
