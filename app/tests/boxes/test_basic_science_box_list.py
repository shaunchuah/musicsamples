import pytest
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from pytest_django.asserts import assertTemplateUsed

from app.factories import BasicScienceBoxFactory
from app.models import BasicScienceBox
from app.views.box_views import BasicScienceBoxListView


@pytest.fixture
def box_list_fixtures():
    return {
        "box1": BasicScienceBoxFactory(is_used=False),
        "box2": BasicScienceBoxFactory(is_used=False),
        "box3": BasicScienceBoxFactory(is_used=True),
    }


@pytest.mark.django_db
def test_view_requires_login(rf, box_list_url):
    request = rf.get(box_list_url)
    request.user = AnonymousUser()

    response = BasicScienceBoxListView.as_view()(request)

    assert response.status_code == 302
    assert "/login/" in response["Location"]


@pytest.mark.django_db
def test_view_requires_permission(rf, box_user, box_list_url):
    request = rf.get(box_list_url)
    request.user = box_user

    view = BasicScienceBoxListView()
    view.request = request

    with pytest.raises(PermissionDenied):
        view.dispatch(request)


@pytest.mark.django_db
def test_view_with_permission(rf, box_user, grant_permission, box_list_url):
    grant_permission(box_user, "view_basicsciencebox")

    request = rf.get(box_list_url)
    request.user = box_user

    response = BasicScienceBoxListView.as_view()(request)

    assert response.status_code == 200


@pytest.mark.django_db
def test_view_uses_correct_template(client, box_user_with_permission, box_list_url):
    client.force_login(box_user_with_permission)

    response = client.get(box_list_url)

    assert response.status_code == 200
    assertTemplateUsed(response, "boxes/box_list.html")


@pytest.mark.django_db
def test_view_context_contains_boxes(client, box_user_with_permission, box_list_url, box_list_fixtures):
    client.force_login(box_user_with_permission)

    response = client.get(box_list_url)
    assert "boxes" in response.context

    boxes = list(response.context["boxes"])
    assert box_list_fixtures["box1"] in boxes
    assert box_list_fixtures["box2"] in boxes
    assert box_list_fixtures["box3"] not in boxes


@pytest.mark.django_db
def test_queryset_excludes_used_boxes(rf, box_user, grant_permission, box_list_url, box_list_fixtures):
    grant_permission(box_user, "view_basicsciencebox")

    request = rf.get(box_list_url)
    request.user = box_user

    view = BasicScienceBoxListView()
    view.request = request

    queryset = view.get_queryset()

    assert box_list_fixtures["box3"] not in queryset
    assert box_list_fixtures["box1"] in queryset
    assert box_list_fixtures["box2"] in queryset


def test_context_object_name():
    view = BasicScienceBoxListView()
    assert view.context_object_name == "boxes"


def test_model_attribute():
    view = BasicScienceBoxListView()
    assert view.model is BasicScienceBox


def test_permission_required_attribute():
    view = BasicScienceBoxListView()
    assert view.permission_required == "app.view_basicsciencebox"
