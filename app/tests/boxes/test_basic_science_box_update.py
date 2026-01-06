import pytest
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from app.views.box_views import BasicScienceBoxUpdateView

from app.choices import BasicScienceGroupChoices

pytestmark = pytest.mark.django_db


@pytest.fixture
def box_update_payload():
    return {
        "box_id": "UPDATED001",
        "basic_science_group": BasicScienceGroupChoices.JONES.value,
        "box_type": "basic_science_samples",
        "location": "sii_freezer_1",
    }


def test_view_requires_login(rf, box_edit_url, basic_science_box):
    request = rf.get(box_edit_url)
    request.user = AnonymousUser()

    response = BasicScienceBoxUpdateView.as_view()(request, pk=basic_science_box.pk)

    assert response.status_code == 302
    assert "/login/" in response["Location"]


def test_view_requires_permission(rf, box_user, box_edit_url, basic_science_box):
    request = rf.get(box_edit_url)
    request.user = box_user

    view = BasicScienceBoxUpdateView()
    view.request = request

    with pytest.raises(PermissionDenied):
        view.dispatch(request, pk=basic_science_box.pk)


def test_view_with_permission_get(rf, box_user, grant_permission, box_edit_url, basic_science_box):
    grant_permission(box_user, "change_basicsciencebox")

    request = rf.get(box_edit_url)
    request.user = box_user

    response = BasicScienceBoxUpdateView.as_view()(request, pk=basic_science_box.pk)

    assert response.status_code == 200


def test_form_valid_updates_box(
    client, box_user, grant_permission, box_edit_url, basic_science_box, box_update_payload
):
    grant_permission(box_user, "change_basicsciencebox")
    client.force_login(box_user)

    response = client.post(box_edit_url, box_update_payload)

    assert response.status_code == 302
    basic_science_box.refresh_from_db()
    assert basic_science_box.box_id == box_update_payload["box_id"]


def test_form_valid_sets_last_modified_by(
    client, box_user, grant_permission, box_edit_url, basic_science_box, box_update_payload
):
    grant_permission(box_user, "change_basicsciencebox")
    client.force_login(box_user)

    client.post(box_edit_url, box_update_payload)

    basic_science_box.refresh_from_db()
    assert basic_science_box.last_modified_by == box_user
