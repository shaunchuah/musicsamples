import pytest
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed

pytestmark = pytest.mark.django_db

User = get_user_model()


class NewUserViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email="testuser@example.com", password="password123", is_staff=True)
        self.client.login(email="testuser@example.com", password="password123")

    def test_new_user_view_post_valid_data(self):
        url = reverse("new_user")
        form_data = {
            "first_name": "Test User 2",
            "last_name": "Test",
            "email": "testuser2@example.com",
        }
        response = self.client.post(url, data=form_data)
        assert response.status_code == 302
        assert response.url == reverse("user_list")
        assert User.objects.filter(email="testuser2@example.com").exists()

    def test_new_user_view_post_invalid_data(self):
        url = reverse("new_user")
        form_data = {"first_name": "", "last_name": "", "email": "invalidemail"}
        response = self.client.post(url, data=form_data)
        assert response.status_code == 200
        assertTemplateUsed(response, "accounts/new_user.html")
        assert "form" in response.context
        assert not User.objects.filter(email="invalidemail").exists()

    def test_new_user_view_post_duplicate_email(self):
        User.objects.create_user(
            first_name="Existing User",
            last_name="Existing User last name",
            email="existinguser@example.com",
            password="password123",
        )
        url = reverse("new_user")
        form_data = {
            "first_name": "New User",
            "last_name": "New User Last Name",
            "email": "existinguser@example.com",
        }
        response = self.client.post(url, data=form_data)
        assert response.status_code == 200
        assertTemplateUsed(response, "accounts/new_user.html")
        assert "form" in response.context
        assert User.objects.filter(email="existinguser@example.com").count() == 1
