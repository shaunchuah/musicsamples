from django.test import TestCase
from django.urls import resolve, reverse

from datasets.views import (
    DatasetAnalyticsCreateUpdateView,
    DatasetCreateUpdateView,
    DataSourceStatusCheckView,
    RetrieveDatasetAPIView,
    dataset_access_history,
    dataset_export_csv,
    list_datasets,
)


class TestUrls(TestCase):
    def test_create_url(self):
        url = reverse("datasets:create")
        self.assertEqual(resolve(url).func.view_class, DatasetCreateUpdateView)
        self.assertEqual(url, "/datasets/api/create/")

    def test_retrieve_url(self):
        url = reverse("datasets:retrieve", args=["test_dataset"])
        self.assertEqual(resolve(url).func.view_class, RetrieveDatasetAPIView)
        self.assertEqual(url, "/datasets/api/retrieve/test_dataset/")

    def test_status_check_url(self):
        url = reverse("datasets:status_check")
        self.assertEqual(resolve(url).func.view_class, DataSourceStatusCheckView)
        self.assertEqual(url, "/datasets/api/status_check/")

    def test_analytics_url(self):
        url = reverse("datasets:analytics")
        self.assertEqual(resolve(url).func.view_class, DatasetAnalyticsCreateUpdateView)
        self.assertEqual(url, "/datasets/api/analytics/")

    def test_list_url(self):
        url = reverse("datasets:list")
        self.assertEqual(resolve(url).func, list_datasets)
        self.assertEqual(url, "/datasets/list/")

    def test_export_csv_url(self):
        url = reverse("datasets:export_csv", args=["test_dataset"])
        self.assertEqual(resolve(url).func, dataset_export_csv)
        self.assertEqual(url, "/datasets/export_csv/test_dataset/")

    def test_access_history_url(self):
        url = reverse("datasets:access_history", args=["test_dataset"])
        self.assertEqual(resolve(url).func, dataset_access_history)
        self.assertEqual(url, "/datasets/access_history/test_dataset/")
