from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.test import Client, TestCase
from django.urls import reverse
from guardian.shortcuts import get_perms

from app.models import DataStore

User = get_user_model()


class DataStorePermissionTests(TestCase):
    def setUp(self):
        # Create users
        self.admin_user = User.objects.create_superuser(email="admin@example.com", password="adminpass")
        self.regular_user1 = User.objects.create_user(email="user1@example.com", password="user1pass")
        self.regular_user2 = User.objects.create_user(email="user2@example.com", password="user2pass")

        content_type = ContentType.objects.get_for_model(DataStore)
        view_permission = Permission.objects.get(
            codename="view_datastore",
            content_type=content_type,
        )

        # Add permissions
        for user in [self.regular_user1, self.regular_user2]:
            user.user_permissions.add(*User.objects.get(email="admin@example.com").user_permissions.all())
            user.user_permissions.add(view_permission)

        # Create test files
        self.file1 = DataStore.objects.create(
            category="DATA",
            study_name="MUSIC",
            original_file_name="file1.txt",
            formatted_file_name="MUSIC_file1.txt",
            upload_finished_at="2023-01-01T12:00:00Z",
            uploaded_by=self.regular_user1,
        )

        self.file2 = DataStore.objects.create(
            category="DATA",
            study_name="MUSIC",
            original_file_name="file2.txt",
            formatted_file_name="MUSIC_file2.txt",
            upload_finished_at="2023-01-01T12:00:00Z",
            uploaded_by=self.regular_user2,
        )

        # Create clients
        self.admin_client = Client()
        self.user1_client = Client()
        self.user2_client = Client()
        self.admin_client.login(email="admin@example.com", password="adminpass")
        self.user1_client.login(email="user1@example.com", password="user1pass")
        self.user2_client.login(email="user2@example.com", password="user2pass")

    def test_permissions_assigned_on_creation(self):
        """Test that object permissions are assigned correctly on file creation"""
        # Check user1's permissions on file1
        self.assertIn("delete_own_datastore", get_perms(self.regular_user1, self.file1))
        self.assertIn("view_datastore", get_perms(self.regular_user1, self.file1))

        # Check user2's permissions on file2
        self.assertIn("delete_own_datastore", get_perms(self.regular_user2, self.file2))
        self.assertIn("view_datastore", get_perms(self.regular_user2, self.file2))

        # Check that user1 doesn't have delete permission on file2
        self.assertNotIn("delete_own_datastore", get_perms(self.regular_user1, self.file2))

        # Check that user2 doesn't have delete permission on file1
        self.assertNotIn("delete_own_datastore", get_perms(self.regular_user2, self.file1))

    @patch("app.views.datastore_views.azure_delete_file")
    def test_owner_can_delete_file(self, mock_azure_delete):
        """Test that file owner can delete their own file"""
        # User1 tries to delete their own file
        response = self.user1_client.get(reverse("datastore_delete", args=[self.file1.id]))

        # Verify azure_delete_file was called with the correct file
        mock_azure_delete.assert_called_once()

        # Check if file is deleted
        self.assertEqual(response.status_code, 302)  # Redirect after successful deletion
        self.assertFalse(DataStore.objects.filter(id=self.file1.id).exists())

    @patch("app.views.datastore_views.azure_delete_file")
    def test_non_owner_cannot_delete_file(self, mock_azure_delete):
        """Test that non-owner cannot delete someone else's file"""
        # User1 tries to delete user2's file
        response = self.user1_client.get(reverse("datastore_delete", args=[self.file2.id]))

        # Verify azure_delete_file was NOT called
        mock_azure_delete.assert_not_called()

        # Check if file still exists
        self.assertEqual(response.status_code, 302)  # Redirects with error message
        self.assertTrue(DataStore.objects.filter(id=self.file2.id).exists())

    @patch("app.views.datastore_views.azure_delete_file")
    def test_admin_can_delete_any_file(self, mock_azure_delete):
        """Test that admin can delete any file"""
        # Admin tries to delete user1's file
        response = self.admin_client.get(reverse("datastore_delete", args=[self.file1.id]))

        # Verify azure_delete_file was called with the correct file
        mock_azure_delete.assert_called_once()

        # Check if file is deleted
        self.assertEqual(response.status_code, 302)  # Redirect after successful deletion
        self.assertFalse(DataStore.objects.filter(id=self.file1.id).exists())
