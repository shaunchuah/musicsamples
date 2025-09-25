import pytest
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.urls import reverse

from app.choices import BasicScienceGroupChoices, SpeciesChoices
from app.factories import BasicScienceSampleTypeFactory, ExperimentalIDFactory, TissueTypeFactory
from app.models import ExperimentalID
from app.views.box_views import (
    ExperimentalIdCreateView,
    ExperimentalIdDeleteView,
    ExperimentalIdDetailView,
    ExperimentalIdListView,
    ExperimentalIdUpdateView,
)

pytestmark = pytest.mark.django_db


def test_experimental_id_list_requires_login(rf):
    url = reverse("boxes:experimental_id_list")
    request = rf.get(url)
    request.user = AnonymousUser()

    response = ExperimentalIdListView.as_view()(request)

    assert response.status_code == 302
    assert "/login/" in response["Location"]


def test_experimental_id_list_shows_active_only(client, box_user, grant_permission):
    url = reverse("boxes:experimental_id_list")
    active = ExperimentalIDFactory()
    deleted = ExperimentalIDFactory(is_deleted=True)
    client.force_login(box_user)
    grant_permission(box_user, "view_basicsciencebox")

    response = client.get(url)

    assert response.status_code == 200
    experiments = list(response.context["experimental_ids"])
    assert active in experiments
    assert deleted not in experiments


def test_experimental_id_create_requires_permission(rf, box_user):
    url = reverse("boxes:experimental_id_create")
    request = rf.get(url)
    request.user = box_user

    view = ExperimentalIdCreateView()
    view.request = request

    with pytest.raises(PermissionDenied):
        view.dispatch(request)


def test_experimental_id_valid_post_creates_experiment(client, box_user, grant_permission):
    url = reverse("boxes:experimental_id_create")
    sample_type = BasicScienceSampleTypeFactory()
    tissue_type = TissueTypeFactory()
    payload = {
        "basic_science_group": BasicScienceGroupChoices.BAIN.value,
        "name": "EXP-CREATE-001",
        "description": "Created via test",
        "date": "2024-01-01",
        "sample_types": [sample_type.pk],
        "tissue_types": [tissue_type.pk],
        "species": SpeciesChoices.HUMAN.value,
    }
    client.force_login(box_user)
    grant_permission(box_user, "add_basicsciencebox")

    response = client.post(url, payload)

    assert response.status_code == 302
    experiment = ExperimentalID.objects.get(name=payload["name"])
    assert experiment.created_by == box_user
    assert experiment.sample_types.filter(pk=sample_type.pk).exists()
    assert experiment.tissue_types.filter(pk=tissue_type.pk).exists()


def test_experimental_id_invalid_post_returns_errors(client, box_user, grant_permission):
    url = reverse("boxes:experimental_id_create")
    client.force_login(box_user)
    grant_permission(box_user, "add_basicsciencebox")

    response = client.post(
        url,
        {"basic_science_group": BasicScienceGroupChoices.BAIN.value, "species": SpeciesChoices.HUMAN.value},
    )

    assert response.status_code == 200
    form = response.context["form"]
    assert "name" in form.errors
    assert "This field is required." in form.errors["name"]


def test_experimental_id_detail_requires_login(rf):
    experiment = ExperimentalIDFactory()
    url = reverse("boxes:experimental_id_detail", kwargs={"pk": experiment.pk})
    request = rf.get(url)
    request.user = AnonymousUser()

    response = ExperimentalIdDetailView.as_view()(request, pk=experiment.pk)

    assert response.status_code == 302
    assert "/login/" in response["Location"]


def test_experimental_id_detail_with_permission(client, box_user, grant_permission):
    experiment = ExperimentalIDFactory()
    url = reverse("boxes:experimental_id_detail", kwargs={"pk": experiment.pk})
    client.force_login(box_user)
    grant_permission(box_user, "view_basicsciencebox")

    response = client.get(url)

    assert response.status_code == 200
    assert response.context["experimental_id"] == experiment
    assert "changes" in response.context


def test_experimental_id_update_requires_permission(rf, box_user):
    experiment = ExperimentalIDFactory()
    url = reverse("boxes:experimental_id_edit", kwargs={"pk": experiment.pk})
    request = rf.get(url)
    request.user = box_user

    view = ExperimentalIdUpdateView()
    view.request = request

    with pytest.raises(PermissionDenied):
        view.dispatch(request, pk=experiment.pk)


def test_experimental_id_update_succeeds(client, box_user, grant_permission):
    experiment = ExperimentalIDFactory(name="EXP-ORIGINAL")
    sample_type = BasicScienceSampleTypeFactory()
    url = reverse("boxes:experimental_id_edit", kwargs={"pk": experiment.pk})
    payload = {
        "basic_science_group": experiment.basic_science_group,
        "name": "EXP-UPDATED",
        "description": "Updated description",
        "date": experiment.date.strftime("%Y-%m-%d") if experiment.date else "2024-01-01",
        "sample_types": [sample_type.pk],
        "tissue_types": [],
        "species": experiment.species,
    }
    client.force_login(box_user)
    grant_permission(box_user, "change_basicsciencebox")

    response = client.post(url, payload)

    assert response.status_code == 302
    experiment.refresh_from_db()
    assert experiment.name == "EXP-UPDATED"
    assert experiment.last_modified_by == box_user


def test_experimental_id_delete_requires_login(rf):
    experiment = ExperimentalIDFactory(is_deleted=False)
    url = reverse("boxes:experimental_id_delete", kwargs={"pk": experiment.pk})
    request = rf.post(url)
    request.user = AnonymousUser()

    response = ExperimentalIdDeleteView.as_view()(request, pk=experiment.pk)

    assert response.status_code == 302
    assert "/login/" in response["Location"]


def test_experimental_id_delete_requires_permission(client, box_user):
    experiment = ExperimentalIDFactory(is_deleted=False)
    url = reverse("boxes:experimental_id_delete", kwargs={"pk": experiment.pk})
    client.force_login(box_user)

    response = client.post(url)

    assert response.status_code == 403


def test_experimental_id_delete_marks_deleted(client, box_user, grant_permission):
    experiment = ExperimentalIDFactory(is_deleted=False)
    url = reverse("boxes:experimental_id_delete", kwargs={"pk": experiment.pk})
    client.force_login(box_user)
    grant_permission(box_user, "delete_basicsciencebox")

    response = client.post(url)

    assert response.status_code == 302
    experiment.refresh_from_db()
    assert experiment.is_deleted is True
    assert experiment.last_modified_by == box_user


def test_experimental_id_restore_requires_permission(client, box_user):
    experiment = ExperimentalIDFactory(is_deleted=True)
    url = reverse("boxes:experimental_id_restore", kwargs={"pk": experiment.pk})
    client.force_login(box_user)

    response = client.post(url)

    assert response.status_code == 403


def test_experimental_id_restore_marks_active(client, box_user, grant_permission):
    experiment = ExperimentalIDFactory(is_deleted=True)
    url = reverse("boxes:experimental_id_restore", kwargs={"pk": experiment.pk})
    client.force_login(box_user)
    grant_permission(box_user, "delete_basicsciencebox")

    response = client.post(url)

    assert response.status_code == 302
    experiment.refresh_from_db()
    assert experiment.is_deleted is False
    assert experiment.last_modified_by == box_user
