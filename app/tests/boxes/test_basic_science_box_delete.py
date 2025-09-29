import pytest
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied

from app.views.box_views import BasicScienceBoxDeleteView

pytestmark = pytest.mark.django_db


def test_view_requires_login(rf, box_delete_url, basic_science_box):
    request = rf.get(box_delete_url)
    request.user = AnonymousUser()

    response = BasicScienceBoxDeleteView.as_view()(request, pk=basic_science_box.pk)

    assert response.status_code == 302
    assert "/login/" in response["Location"]


def test_view_requires_permission(rf, box_user, box_delete_url, basic_science_box):
    request = rf.get(box_delete_url)
    request.user = box_user

    view = BasicScienceBoxDeleteView()
    view.request = request

    with pytest.raises(PermissionDenied):
        view.dispatch(request, pk=basic_science_box.pk)


def test_post_marks_box_used(client, box_user, grant_permission, box_delete_url, basic_science_box):
    grant_permission(box_user, "delete_basicsciencebox")
    client.force_login(box_user)

    response = client.post(box_delete_url)

    assert response.status_code == 302
    basic_science_box.refresh_from_db()
    assert basic_science_box.is_used


def test_post_sets_last_modified_by(client, box_user, grant_permission, box_delete_url, basic_science_box):
    grant_permission(box_user, "delete_basicsciencebox")
    client.force_login(box_user)

    client.post(box_delete_url)

    basic_science_box.refresh_from_db()
    assert basic_science_box.last_modified_by == box_user


def test_post_adds_success_message(client, box_user, grant_permission, box_delete_url):
    grant_permission(box_user, "delete_basicsciencebox")
    client.force_login(box_user)

    response = client.post(box_delete_url, follow=True)

    messages = list(response.context["messages"])
    assert len(messages) == 1
    assert str(messages[0]) == "Box deleted successfully."
