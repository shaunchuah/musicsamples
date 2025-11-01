import json

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.test import Client, TestCase
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from pytest_django.asserts import assertTemplateUsed

pytestmark = pytest.mark.django_db

User = get_user_model()


class NewUserViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email="testuser@example.com", password="password123", is_staff=True)  # type:ignore
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
        assert response.url == reverse("user_list")  # type:ignore
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
        )  # type:ignore
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


class PasswordResetApiTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("password_reset_api")

    def test_password_reset_api_sends_email_for_valid_user(self):
        user = User.objects.create_user(email="reset@example.com", password="password123")  # type:ignore

        response = self.client.post(
            self.url,
            data=json.dumps({"email": user.email}),
            content_type="application/json",
        )

        assert response.status_code == 200
        assert response.json() == {"success": True}
        assert len(mail.outbox) == 1
        assert mail.outbox[0].to == [user.email]

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        assert f"/reset-password/{uid}/" in mail.outbox[0].body

    def test_password_reset_api_rejects_invalid_email(self):
        response = self.client.post(
            self.url,
            data=json.dumps({"email": "not-an-email"}),
            content_type="application/json",
        )

        assert response.status_code == 400
        assert response.json()["error"] == "Enter a valid email address."
        assert len(mail.outbox) == 0


class PasswordResetConfirmApiTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("password_reset_confirm_api")
        self.user = User.objects.create_user(email="confirm@example.com", password="initial123")
        self.uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.token = default_token_generator.make_token(self.user)

    def test_password_reset_confirm_api_updates_password(self):
        payload = {
            "uid": self.uid,
            "token": self.token,
            "new_password": "newstrongpass1",
        }

        response = self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type="application/json",
        )

        assert response.status_code == 200
        assert response.json() == {"success": True}
        self.user.refresh_from_db()
        assert self.user.check_password("newstrongpass1")

    def test_password_reset_confirm_api_rejects_invalid_token(self):
        payload = {
            "uid": self.uid,
            "token": "invalid-token",
            "new_password": "anotherStrong1",
        }

        response = self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type="application/json",
        )

        assert response.status_code == 400
        assert response.json()["error"] == "Reset link is invalid or has expired."

    def test_password_reset_confirm_api_enforces_password_policy(self):
        payload = {
            "uid": self.uid,
            "token": self.token,
            "new_password": "short",
        }

        response = self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type="application/json",
        )

        assert response.status_code == 400
        assert response.json()["error"]
