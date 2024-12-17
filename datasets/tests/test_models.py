import pytest
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.test import TestCase

from datasets.factories import DatasetFactory
from datasets.models import (
    Dataset,
    DatasetAccessHistory,
    DatasetAccessTypeChoices,
    DatasetAnalytics,
    DataSourceStatusCheck,
)

pytestmark = pytest.mark.django_db


class TestDatasetModel(TestCase):
    def test_str_method(self):
        dataset = DatasetFactory(name="test001")
        assert dataset.__str__() == "test001"


class TestDatasetAnalyticsModel(TestCase):
    def test_str_method(self):
        analytics = DatasetAnalytics.objects.create(name="test_analytics")
        assert str(analytics) == "test_analytics"

    def test_verbose_name_plural(self):
        assert DatasetAnalytics._meta.verbose_name_plural == "Dataset analytics"

    def test_unique_name_constraint(self):
        DatasetAnalytics.objects.create(name="unique_name")
        with pytest.raises(IntegrityError):
            DatasetAnalytics.objects.create(name="unique_name")


class TestDatasetAccessHistoryModel(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(email="testuser@test.com", password="testpass123")
        self.dataset = DatasetFactory()
        self.access_history = DatasetAccessHistory.objects.create(dataset=self.dataset, user=self.user)

    def test_str_method(self):
        expected = (
            f"{self.user} accessed {self.dataset} on {self.access_history.accessed.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        assert str(self.access_history) == expected

    def test_default_access_type(self):
        assert self.access_history.access_type == DatasetAccessTypeChoices.NOT_RECORDED

    def test_verbose_name_plural(self):
        assert DatasetAccessHistory._meta.verbose_name_plural == "Dataset access histories"

    def test_relationships(self):
        assert isinstance(self.access_history.dataset, Dataset)
        assert isinstance(self.access_history.user, get_user_model())


class TestDataSourceStatusCheckModel(TestCase):
    def setUp(self):
        self.status_check = DataSourceStatusCheck.objects.create(data_source="test_api", response_status=200)

    def test_str_method(self):
        expected = f"API check for {self.status_check.data_source} at {self.status_check.checked_at.strftime('%Y-%m-%d %H:%M:%S')}"
        assert str(self.status_check) == expected

    def test_nullable_error_message(self):
        status_check = DataSourceStatusCheck.objects.create(
            data_source="test_api", response_status=500, error_message="Internal Server Error"
        )
        assert status_check.error_message == "Internal Server Error"

    def test_basic_creation(self):
        assert self.status_check.data_source == "test_api"
        assert self.status_check.response_status == 200
        assert self.status_check.error_message is None
