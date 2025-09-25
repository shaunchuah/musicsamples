from unittest.mock import patch

import pytest
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed

from app.factories import (
    BasicScienceBoxFactory,
    BasicScienceSampleTypeFactory,
    ExperimentalIDFactory,
    TissueTypeFactory,
)
from app.models import BasicScienceBox
from app.views.box_views import BasicScienceBoxDetailView


@pytest.mark.django_db
def test_view_requires_login(rf, box_detail_url, basic_science_box):
    request = rf.get(box_detail_url)
    request.user = AnonymousUser()

    response = BasicScienceBoxDetailView.as_view()(request, pk=basic_science_box.pk)

    assert response.status_code == 302
    assert "/login/" in response["Location"]


@pytest.mark.django_db
def test_view_requires_permission(rf, box_user, box_detail_url, basic_science_box):
    request = rf.get(box_detail_url)
    request.user = box_user

    view = BasicScienceBoxDetailView()
    view.request = request

    with pytest.raises(PermissionDenied):
        view.dispatch(request, pk=basic_science_box.pk)


@pytest.mark.django_db
def test_view_with_permission(rf, box_user, grant_permission, box_detail_url, basic_science_box):
    grant_permission(box_user, "view_basicsciencebox")

    request = rf.get(box_detail_url)
    request.user = box_user

    response = BasicScienceBoxDetailView.as_view()(request, pk=basic_science_box.pk)

    assert response.status_code == 200


@pytest.mark.django_db
def test_view_uses_correct_template(client, box_user_with_permission, box_detail_url):
    client.force_login(box_user_with_permission)

    response = client.get(box_detail_url)

    assert response.status_code == 200
    assertTemplateUsed(response, "boxes/box_detail.html")


@pytest.mark.django_db
def test_view_context_contains_box(client, box_user_with_permission, box_detail_url, basic_science_box):
    client.force_login(box_user_with_permission)

    response = client.get(box_detail_url)

    assert "box" in response.context
    assert response.context["box"].pk == basic_science_box.pk


@pytest.mark.django_db
def test_view_context_contains_changes(client, box_user_with_permission, box_detail_url):
    client.force_login(box_user_with_permission)

    response = client.get(box_detail_url)

    assert "changes" in response.context
    assert "first" in response.context
    assert isinstance(response.context["changes"], list)


@pytest.mark.django_db
def test_view_with_nonexistent_box(client, box_user_with_permission):
    client.force_login(box_user_with_permission)

    response = client.get(reverse("boxes:detail", kwargs={"pk": 99999}))

    assert response.status_code == 404


def test_context_object_name():
    view = BasicScienceBoxDetailView()
    assert view.context_object_name == "box"


def test_model_attribute():
    view = BasicScienceBoxDetailView()
    assert view.model is BasicScienceBox


def test_permission_required_attribute():
    view = BasicScienceBoxDetailView()
    assert view.permission_required == "app.view_basicsciencebox"


@pytest.mark.django_db
@patch.object(BasicScienceBoxDetailView, "get_object")
def test_get_context_data_method(mock_get_object, rf, box_user_with_permission):
    box = BasicScienceBoxFactory()

    mock_get_object.return_value = box

    view = BasicScienceBoxDetailView()
    request = rf.get(reverse("boxes:detail", kwargs={"pk": box.pk}))
    request.user = box_user_with_permission
    view.request = request
    view.object = box  # type: ignore[assignment]

    context = view.get_context_data()

    assert context["box"] == box
    assert "changes" in context
    assert "first" in context
    assert isinstance(context["changes"], list)


@pytest.mark.django_db
def test_distinct_sample_and_tissue_labels_helpers():
    sample_type = BasicScienceSampleTypeFactory()
    tissue_type = TissueTypeFactory()
    experimental = ExperimentalIDFactory()
    experimental.sample_types.add(sample_type)
    experimental.tissue_types.add(tissue_type)
    box = BasicScienceBoxFactory(experimental_ids=[experimental])

    assert sample_type.label or sample_type.name in box.get_sample_type_labels()
    assert tissue_type.label or tissue_type.name in box.get_tissue_type_labels()
