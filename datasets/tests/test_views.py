import json

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from datasets.models import Dataset, DatasetAnalytics

User = get_user_model()
pytestmark = pytest.mark.django_db


class TestDatasetApiViews(TestCase):
    def setUp(self):
        self.client = APIClient()
        # need to be admin to create datasets
        self.user_with_permission = User.objects.create_superuser(email="privileged@user.com", password="12345")
        self.client.login(username="privileged@user.com", password="12345")
        self.json_object = json.dumps({"key": "value"})

    def test_create_dataset_api_view(self):
        url = reverse("datasets:create")
        data = {
            "name": "test_dataset",
            "description": "test description",
            "json": self.json_object,
            "study_name": "gidamps",
        }

        response = self.client.post(url, data)

        assert response.status_code == status.HTTP_201_CREATED
        assert Dataset.objects.count() == 1
        assert Dataset.objects.get(name="test_dataset").json == json.loads(data["json"])

    def test_retrieve_dataset_api_view(self):
        dataset = Dataset.objects.create(name="test_dataset", json=self.json_object)
        url = reverse("datasets:retrieve", kwargs={"name": dataset.name})
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert json.loads(response.json()) == json.loads(self.json_object)

    def test_create_dataset_api_view_with_existing_object(self):
        Dataset.objects.create(name="test_dataset", description="initial", json=self.json_object)
        assert Dataset.objects.get(name="test_dataset").description == "initial"
        url = reverse("datasets:create")
        data = {
            "name": "test_dataset",
            "description": "updated description",
            "json": self.json_object,
            "study_name": "gidamps",
        }

        response = self.client.post(url, data)

        assert response.status_code == status.HTTP_200_OK
        assert Dataset.objects.count() == 1
        assert Dataset.objects.get(name="test_dataset").description == "updated description"


class TestDatasetDjangoViewsAuthorized(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_with_permission = User.objects.create_user(email="privileged@user.com", password="12345")
        permission = Permission.objects.get(codename="view_dataset")
        self.user_with_permission.user_permissions.add(permission)
        self.client.login(username="privileged@user.com", password="12345")

    def test_list_datasets_view(self):
        url = reverse("datasets:list")
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_dataset_export_csv_view(self):
        dataset = Dataset.objects.create(name="test_dataset", json={"key": "value"})
        url = reverse("datasets:export_csv", kwargs={"dataset_name": dataset.name})
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK


class TestDatasetDjangoViewsUnauthorized(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email="test@newuser.com", password="12345")
        self.client.login(username="test@newuser.com", password="12345")

    def test_list_datasets_view(self):
        url = reverse("datasets:list")
        response = self.client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert b"Forbidden" in response.content

    def test_dataset_export_csv_view(self):
        dataset = Dataset.objects.create(name="test_dataset", json={"key": "value"})
        url = reverse("datasets:export_csv", kwargs={"dataset_name": dataset.name})
        response = self.client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert b"Forbidden" in response.content


class TestDatasetAnalyticsApiViews(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_with_permission = User.objects.create_superuser(email="privileged@user.com", password="12345")
        self.client.login(username="privileged@user.com", password="12345")
        self.analytics_data = {
            "name": "test_analytics",
            "data": {"stats": "test_stats"},
        }

    def test_create_dataset_analytics(self):
        url = reverse("datasets:analytics")
        response = self.client.post(url, self.analytics_data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert DatasetAnalytics.objects.count() == 1
        analytics = DatasetAnalytics.objects.get(name="test_analytics")
        assert analytics.data == self.analytics_data["data"]

    def test_update_dataset_analytics(self):
        # Create initial analytics
        DatasetAnalytics.objects.create(
            name="test_analytics",
            data={"stats": "initial_stats"},
        )

        # Update data
        updated_data = self.analytics_data.copy()
        updated_data["data"] = {"stats": "updated_stats"}

        url = reverse("datasets:analytics")
        response = self.client.post(url, updated_data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert DatasetAnalytics.objects.count() == 1
        analytics = DatasetAnalytics.objects.get(name="test_analytics")
        assert analytics.data == {"stats": "updated_stats"}

    def test_create_dataset_analytics_unauthorized(self):
        # Create non-admin user
        self.client.logout()
        User.objects.create_user(email="regular@user.com", password="12345")
        self.client.login(username="regular@user.com", password="12345")

        url = reverse("datasets:analytics")
        response = self.client.post(url, self.analytics_data, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN
