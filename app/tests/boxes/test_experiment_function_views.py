import pytest
from django.urls import reverse

from app.factories import ExperimentFactory

pytestmark = pytest.mark.django_db


def test_experiment_search_requires_login(client):
    response = client.get(reverse("boxes:experiment_search"), {"q": "Search"})

    assert response.status_code == 302


def test_experiment_search_returns_matches(client, box_user, grant_permission):
    match = ExperimentFactory(name="Search Target", description="Interesting experiment")
    ExperimentFactory(name="Background", description="Other")
    client.force_login(box_user)
    grant_permission(box_user, "view_basicsciencebox")

    response = client.get(reverse("boxes:experiment_search"), {"q": "Search"})

    assert response.status_code == 200
    assert match in response.context["experiments"]


def test_export_experiments_csv(client, box_user, grant_permission):
    experiment = ExperimentFactory(name="CSV Target")
    client.force_login(box_user)
    grant_permission(box_user, "view_basicsciencebox")

    response = client.get(reverse("boxes:experiment_export_csv"), {"q": experiment.name})

    assert response.status_code == 200
    assert response["Content-Type"] == "text/csv"


def test_experiment_filter_requires_permission(client, box_user):
    client.force_login(box_user)

    response = client.get(reverse("boxes:experiment_filter"))

    assert response.status_code == 403


def test_experiment_filter_returns_context(client, box_user, grant_permission):
    client.force_login(box_user)
    grant_permission(box_user, "view_basicsciencebox")

    response = client.get(reverse("boxes:experiment_filter"))

    assert response.status_code == 200
    assert "experiment_filter" in response.context


def test_experiment_filter_export_csv(client, box_user, grant_permission):
    client.force_login(box_user)
    grant_permission(box_user, "view_basicsciencebox")

    response = client.get(reverse("boxes:experiment_filter_export_csv"))

    assert response.status_code == 200
    assert response["Content-Type"] == "text/csv"
