import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.test import Client
from django.urls import reverse

from app.choices import FileCategoryChoices, StudyNameChoices
from app.models import DataStore

User = get_user_model()


@pytest.mark.django_db
class TestDataStoreViews:
    @pytest.fixture(autouse=True)
    def setup_class(self):
        """Setup test data and permissions that will be used by all tests."""
        # Create a test user with basic permissions
        self.user = User.objects.create_user(email="testuser@test.com", password="testpass")  # type:ignore
        content_type = ContentType.objects.get_for_model(DataStore)
        view_permission = Permission.objects.get(content_type=content_type, codename="view_datastore")
        self.user.user_permissions.add(view_permission)

        # Create test data for DataStore
        self.ds1 = DataStore.objects.create(
            study_name=StudyNameChoices.GIDAMPS.value,
            category=FileCategoryChoices.ENDOSCOPY_VIDEOS.value,
            file_type="mov",
            original_file_name="testfile1.mov",
            formatted_file_name="Study1_testfile1_abcd123.mov",
            uploaded_by=self.user,
        )

        self.ds2 = DataStore.objects.create(
            study_name=StudyNameChoices.MUSIC.value,
            category=FileCategoryChoices.UNCATEGORISED.value,
            file_type="txt",
            original_file_name="unique_filename.txt",
            formatted_file_name="Study2_unique_filename_efgh456.txt",
            uploaded_by=self.user,
        )

        # Create client and log in
        self.client = Client()
        self.client.login(username="testuser@test.com", password="testpass")

    @pytest.fixture
    def admin_user(self):
        """Create a user with delete permissions for tests that need it."""
        content_type = ContentType.objects.get_for_model(DataStore)
        delete_permission = Permission.objects.get(content_type=content_type, codename="delete_datastore")
        self.user.user_permissions.add(delete_permission)
        return self.user

    def test_datastore_list_view_get_context_data(self):
        response = self.client.get(reverse("datastore:list"))

        # Check that the response status is 200 OK.
        assert response.status_code == 200

        # Verify the context includes 'datastores' and that it matches the test instances.
        datastores = response.context["datastores"]
        retrieved_ids = {ds.pk for ds in datastores}
        expected_ids = {self.ds1.pk, self.ds2.pk}
        assert retrieved_ids == expected_ids

        # Verify the template used
        assert "datastore/datastore_list.html" in [t.name for t in response.templates]

    def test_datastore_search_view_with_query(self):
        # Test search with query that should match ds2
        response = self.client.get(reverse("datastore:search") + "?q=unique")

        assert response.status_code == 200

        # Verify the context includes only the matching datastore
        datastores = response.context["datastores"]
        assert len(datastores) == 1
        assert datastores[0].pk == self.ds2.pk

        # Verify query_string is passed to context
        assert response.context["query_string"] == "unique"

    def test_datastore_search_view_without_query(self):
        # Test search without query - should redirect to datastore_list
        response = self.client.get(reverse("datastore:search"))

        assert response.status_code == 302
        assert response.url == reverse("datastore:list")  # type:ignore

    def test_datastore_filter_view(self):
        # Test filter by study name
        response = self.client.get(reverse("datastore:filter") + f"?study_name={StudyNameChoices.MUSIC.value}")

        assert response.status_code == 200

        # Check that the filtered results are correct
        datastores = response.context["datastores"]
        assert len(datastores) == 1
        assert datastores[0].pk == self.ds2.pk

        # Check for presence of filter form and parameter string
        assert "datastore_filter" in response.context
        assert "parameter_string" in response.context

    def test_datastore_search_export_csv(self):
        # Test export all
        response = self.client.get(reverse("datastore:search_export_csv"))

        # Check it returns CSV response
        assert response.status_code == 200
        assert response["Content-Type"] == "text/csv"
        assert 'attachment; filename="gtrac_files' in response["Content-Disposition"]

        # Test export with search query
        response = self.client.get(reverse("datastore:search_export_csv") + "?q=testfile1")

        assert response.status_code == 200
        assert response["Content-Type"] == "text/csv"

    def test_datastore_filter_export_csv(self):
        # Test filtered export
        response = self.client.get(
            reverse("datastore:filter_export_csv") + f"?study_name={StudyNameChoices.MUSIC.value}"
        )

        assert response.status_code == 200
        assert response["Content-Type"] == "text/csv"
        assert 'attachment; filename="filtered_files' in response["Content-Disposition"]

    def test_datastore_delete_view(self, admin_user, monkeypatch):
        # Mock the azure_delete_file function
        def mock_azure_delete_file(file):
            return True

        monkeypatch.setattr("app.views.datastore_views.azure_delete_file", mock_azure_delete_file)

        # Test delete view
        response = self.client.post(reverse("datastore:delete", kwargs={"id": self.ds1.id}))  # type:ignore

        # Check redirect
        assert response.status_code == 302
        assert response.url == reverse("datastore:list")  # type:ignore

        # Check file was deleted
        assert not DataStore.objects.filter(id=self.ds1.id).exists()  # type:ignore

    def test_permission_required_for_views(self):
        # Create user without permissions
        User.objects.create_user(email="noperm@test.com", password="testpass")  # type:ignore

        # Create client and log in
        client = Client()
        client.login(username="noperm@test.com", password="testpass")

        # Try to access views that require permission
        list_response = client.get(reverse("datastore:list"))
        create_response = client.get(reverse("datastore:create"))
        filter_response = client.get(reverse("datastore:filter"))

        # All should return 403 Forbidden
        assert list_response.status_code == 403
        assert create_response.status_code == 403
        assert filter_response.status_code == 403
