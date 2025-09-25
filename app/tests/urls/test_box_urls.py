import pytest
from django.urls import resolve, reverse

from app.views.box_views import (
    ExperimentalIdCreateView,
    ExperimentalIdDeleteView,
    ExperimentalIdDetailView,
    ExperimentalIdListView,
    ExperimentalIdRestoreView,
    ExperimentalIdUpdateView,
    box_filter,
    box_filter_export_csv,
    box_search,
    create_experimental_id,
    experiment_filter,
    experiment_search,
    experimental_id_filter_export_csv,
    export_boxes_csv,
    export_experiments_csv,
)


@pytest.mark.parametrize(
    ("name", "kwargs", "url_name"),
    [
        ("boxes:list", None, "list"),
        ("boxes:create", None, "create"),
        ("boxes:detail", {"pk": 1}, "detail"),
        ("boxes:edit", {"pk": 1}, "edit"),
        ("boxes:delete", {"pk": 1}, "delete"),
    ],
)
def test_box_named_routes(name, kwargs, url_name):
    resolved = resolve(reverse(name, kwargs=kwargs or {}))

    assert resolved.url_name == url_name
    assert resolved.namespace == "boxes"


@pytest.mark.parametrize(
    ("name", "kwargs", "expected"),
    [
        ("boxes:filter", None, box_filter),
        ("boxes:filter_export_csv", None, box_filter_export_csv),
        ("boxes:search", None, box_search),
        ("boxes:export_csv", None, export_boxes_csv),
        ("boxes:create_experimental_id", None, create_experimental_id),
        ("boxes:experimental_id_search", None, experiment_search),
        ("boxes:experimental_id_export_csv", None, export_experiments_csv),
        ("boxes:experimental_id_filter", None, experiment_filter),
        ("boxes:experimental_id_filter_export_csv", None, experimental_id_filter_export_csv),
    ],
)
def test_box_function_views(name, kwargs, expected):
    assert resolve(reverse(name, kwargs=kwargs or {})).func is expected


@pytest.mark.parametrize(
    ("name", "kwargs", "view_class"),
    [
        ("boxes:experimental_id_list", None, ExperimentalIdListView),
        ("boxes:experimental_id_create", None, ExperimentalIdCreateView),
        ("boxes:experimental_id_detail", {"pk": 1}, ExperimentalIdDetailView),
        ("boxes:experimental_id_edit", {"pk": 1}, ExperimentalIdUpdateView),
        ("boxes:experimental_id_delete", {"pk": 1}, ExperimentalIdDeleteView),
        ("boxes:experimental_id_restore", {"pk": 1}, ExperimentalIdRestoreView),
    ],
)
def test_experimental_id_class_based_views(name, kwargs, view_class):
    resolved = resolve(reverse(name, kwargs=kwargs or {}))

    assert resolved.func.view_class is view_class  # type: ignore[attr-defined]
    assert resolved.namespace == "boxes"
