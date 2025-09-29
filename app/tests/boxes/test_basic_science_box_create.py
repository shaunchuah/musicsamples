import pytest
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.urls import reverse, reverse_lazy
from pytest_django.asserts import assertTemplateUsed

from app.forms import BasicScienceBoxForm
from app.models import BasicScienceBox
from app.views.box_views import BasicScienceBoxCreateView

pytestmark = pytest.mark.django_db


@pytest.fixture
def box_valid_payload():
    return {
        "box_id": "TEST001",
        "box_type": "basic_science_samples",
        "location": "sii_freezer_1",
    }


def test_view_requires_login(rf, box_create_url):
    request = rf.get(box_create_url)
    request.user = AnonymousUser()

    response = BasicScienceBoxCreateView.as_view()(request)

    assert response.status_code == 302
    assert "/login/" in response["Location"]


def test_view_requires_permission(rf, box_user, box_create_url):
    request = rf.get(box_create_url)
    request.user = box_user

    view = BasicScienceBoxCreateView()
    view.request = request

    with pytest.raises(PermissionDenied):
        view.dispatch(request)


def test_view_with_permission_get(rf, box_user, grant_permission, box_create_url):
    grant_permission(box_user, "add_basicsciencebox")

    request = rf.get(box_create_url)
    request.user = box_user

    response = BasicScienceBoxCreateView.as_view()(request)

    assert response.status_code == 200


def test_view_uses_correct_template(client, box_user, grant_permission, box_create_url):
    grant_permission(box_user, "add_basicsciencebox")
    client.force_login(box_user)

    response = client.get(box_create_url)

    assert response.status_code == 200
    assertTemplateUsed(response, "boxes/box_form.html")


def test_form_valid_creates_box(client, box_user, grant_permission, box_create_url, box_valid_payload):
    grant_permission(box_user, "add_basicsciencebox")
    client.force_login(box_user)

    initial_count = BasicScienceBox.objects.count()

    response = client.post(box_create_url, box_valid_payload)

    assert response.status_code == 302
    assert BasicScienceBox.objects.count() == initial_count + 1


def test_form_valid_sets_audit_fields(client, box_user, grant_permission, box_create_url, box_valid_payload):
    grant_permission(box_user, "add_basicsciencebox")
    client.force_login(box_user)

    client.post(box_create_url, box_valid_payload)

    box = BasicScienceBox.objects.get(box_id=box_valid_payload["box_id"])
    assert box.created_by == box_user
    assert box.last_modified_by == box_user


def test_form_valid_success_message(client, box_user, grant_permission, box_create_url, box_valid_payload):
    grant_permission(box_user, "add_basicsciencebox")
    client.force_login(box_user)

    response = client.post(box_create_url, box_valid_payload, follow=True)

    messages = list(response.context["messages"])
    assert len(messages) == 1
    assert str(messages[0]) == "Box registered successfully."


def test_form_valid_redirects_to_list(client, box_user, grant_permission, box_create_url, box_valid_payload):
    grant_permission(box_user, "add_basicsciencebox")
    client.force_login(box_user)

    response = client.post(box_create_url, box_valid_payload)

    assert response.status_code == 302
    assert response["Location"] == reverse("boxes:list")


def test_form_invalid_returns_errors(client, box_user, grant_permission, box_create_url):
    grant_permission(box_user, "add_basicsciencebox")
    client.force_login(box_user)

    initial = BasicScienceBox.objects.count()

    response = client.post(box_create_url, {"box_id": "TEST001"})

    assert response.status_code == 200
    assert BasicScienceBox.objects.count() == initial
    assert response.context["form"].errors


def test_model_attribute():
    view = BasicScienceBoxCreateView()
    assert view.model is BasicScienceBox


def test_form_class_attribute():
    view = BasicScienceBoxCreateView()
    assert view.form_class is BasicScienceBoxForm


def test_success_url_attribute():
    view = BasicScienceBoxCreateView()
    assert view.success_url == reverse_lazy("boxes:list")


def test_permission_required_attribute():
    view = BasicScienceBoxCreateView()
    assert view.permission_required == "app.add_basicsciencebox"
