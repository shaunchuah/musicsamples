import pytest
from django.urls import resolve, reverse

from app.views.box_views import (
    ExperimentCreateView,
    ExperimentDeleteView,
    ExperimentDetailView,
    ExperimentListView,
    ExperimentRestoreView,
    ExperimentUpdateView,
    box_filter,
    box_filter_export_csv,
    box_search,
    create_experiment,
    experiment_filter,
    experiment_filter_export_csv,
    experiment_search,
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
        ("boxes:create_experiment", None, create_experiment),
        ("boxes:experiment_search", None, experiment_search),
        ("boxes:experiment_export_csv", None, export_experiments_csv),
        ("boxes:experiment_filter", None, experiment_filter),
        ("boxes:experiment_filter_export_csv", None, experiment_filter_export_csv),
    ],
)
def test_box_function_views(name, kwargs, expected):
    assert resolve(reverse(name, kwargs=kwargs or {})).func is expected


@pytest.mark.parametrize(
    ("name", "kwargs", "view_class"),
    [
        ("boxes:experiment_list", None, ExperimentListView),
        ("boxes:experiment_create", None, ExperimentCreateView),
        ("boxes:experiment_detail", {"pk": 1}, ExperimentDetailView),
        ("boxes:experiment_edit", {"pk": 1}, ExperimentUpdateView),
        ("boxes:experiment_delete", {"pk": 1}, ExperimentDeleteView),
        ("boxes:experiment_restore", {"pk": 1}, ExperimentRestoreView),
    ],
)
def test_experiment_class_based_views(name, kwargs, view_class):
    resolved = resolve(reverse(name, kwargs=kwargs or {}))

    assert resolved.func.view_class is view_class  # type: ignore[attr-defined]
    assert resolved.namespace == "boxes"
