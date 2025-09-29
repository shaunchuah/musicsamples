import pytest
from django.urls import reverse

from app.choices import BasicScienceGroupChoices
from app.factories import BasicScienceBoxFactory, ExperimentFactory

pytestmark = pytest.mark.django_db


def test_box_search_with_query(client, box_user_with_permission):
    target_box = BasicScienceBoxFactory()
    client.force_login(box_user_with_permission)

    response = client.get(reverse("boxes:search"), {"q": target_box.box_id})

    assert response.status_code == 200
    assert target_box in response.context["boxes"]
    assert "box_count" in response.context
    assert response.context["box_count"] >= 1


def test_box_search_matches_basic_science_group(client, box_user_with_permission):
    experiments = ExperimentFactory(basic_science_group=BasicScienceGroupChoices.BAIN)
    group_box = BasicScienceBoxFactory(experiments=[experiments])
    client.force_login(box_user_with_permission)

    response = client.get(reverse("boxes:search"), {"q": BasicScienceGroupChoices.BAIN.value})

    assert response.status_code == 200
    assert group_box in response.context["boxes"]


def test_box_search_no_query(client, box_user_with_permission):
    client.force_login(box_user_with_permission)

    response = client.get(reverse("boxes:search"))

    assert response.status_code == 200
    assert response.context["query_string"] == "Null"
    assert "box_count" in response.context


def test_box_search_with_include_used_boxes(client, box_user_with_permission):
    used_box = BasicScienceBoxFactory(is_used=True)
    client.force_login(box_user_with_permission)

    response = client.get(reverse("boxes:search"), {"q": used_box.box_id, "include_used_boxes": "1"})

    assert response.status_code == 200
    assert used_box in response.context["boxes"]


def test_export_boxes_csv_with_query(client, box_user_with_permission):
    box = BasicScienceBoxFactory()
    client.force_login(box_user_with_permission)

    response = client.get(reverse("boxes:export_csv"), {"q": box.box_id})

    assert response.status_code == 200
    assert response["Content-Type"] == "text/csv"


def test_export_boxes_csv_no_query(client, box_user_with_permission):
    client.force_login(box_user_with_permission)

    response = client.get(reverse("boxes:export_csv"))

    assert response.status_code == 200
    assert response["Content-Type"] == "text/csv"


def test_export_boxes_csv_with_include_used_boxes(client, box_user_with_permission):
    used_box = BasicScienceBoxFactory(is_used=True)
    client.force_login(box_user_with_permission)

    response = client.get(reverse("boxes:export_csv"), {"q": used_box.box_id, "include_used_boxes": "1"})

    assert response.status_code == 200
    assert response["Content-Type"] == "text/csv"


def test_box_filter(client, box_user_with_permission):
    client.force_login(box_user_with_permission)

    response = client.get(reverse("boxes:filter"))

    assert response.status_code == 200
    assert "box_filter" in response.context


def test_box_filter_filters_by_basic_science_group(client, box_user_with_permission):
    target_exp = ExperimentFactory(basic_science_group=BasicScienceGroupChoices.BAIN)
    included_box = BasicScienceBoxFactory(experiments=[target_exp])
    other_box = BasicScienceBoxFactory(
        experiments=[ExperimentFactory(basic_science_group=BasicScienceGroupChoices.JONES)]
    )
    client.force_login(box_user_with_permission)

    response = client.get(reverse("boxes:filter"), {"basic_science_group": BasicScienceGroupChoices.BAIN.value})

    page = list(response.context["box_list"])
    assert included_box in page
    assert other_box not in page


def test_box_filter_pagination(client, box_user_with_permission):
    client.force_login(box_user_with_permission)
    for _ in range(30):
        BasicScienceBoxFactory(created_by=box_user_with_permission, last_modified_by=box_user_with_permission)

    response = client.get(reverse("boxes:filter"), {"page": 2})

    assert response.status_code == 200
    assert len(response.context["box_list"]) > 0


def test_box_filter_export_csv(client, box_user_with_permission):
    client.force_login(box_user_with_permission)

    response = client.get(reverse("boxes:filter_export_csv"))

    assert response.status_code == 200
    assert response["Content-Type"] == "text/csv"
