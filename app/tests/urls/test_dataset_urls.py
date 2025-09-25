from django.urls import resolve, reverse

from datasets.views import dataset_access_history, dataset_export_csv, list_datasets


def test_dataset_named_routes():
    for name, url_name in [
        ("datasets:create", "create"),
        ("datasets:status_check", "status_check"),
        ("datasets:analytics", "analytics"),
    ]:
        resolved = resolve(reverse(name))
        assert resolved.url_name == url_name
        assert resolved.namespace == "datasets"


def test_dataset_retrieve_route():
    resolved = resolve(reverse("datasets:retrieve", kwargs={"name": "test"}))
    assert resolved.url_name == "retrieve"
    assert resolved.namespace == "datasets"


def test_dataset_list_url_resolves():
    assert resolve(reverse("datasets:list")).func is list_datasets


def test_dataset_download_helpers():
    assert resolve(reverse("datasets:export_csv", kwargs={"dataset_name": "test"})).func is dataset_export_csv
    assert resolve(reverse("datasets:access_history", kwargs={"dataset_name": "test"})).func is dataset_access_history
