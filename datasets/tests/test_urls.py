from django.urls import resolve, reverse

from datasets.views import DatasetCreateUpdateView, RetrieveDatasetAPIView, dataset_export_csv, list_datasets


def test_dataset_create_update_url():
    path = reverse("datasets:create")
    assert resolve(path).func.view_class == DatasetCreateUpdateView


def test_retrieve_dataset_url():
    path = reverse("datasets:retrieve", kwargs={"name": "test_dataset"})
    assert resolve(path).func.view_class == RetrieveDatasetAPIView


def test_list_datasets_url():
    path = reverse("datasets:list")
    assert resolve(path).func == list_datasets


def test_dataset_export_csv_url():
    path = reverse("datasets:export_csv", kwargs={"dataset_name": "test_dataset"})
    assert resolve(path).func == dataset_export_csv
