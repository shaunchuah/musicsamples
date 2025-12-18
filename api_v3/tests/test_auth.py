# api_v3/tests/test_auth_and_users.py
# Covers api_v3 authentication and user profile endpoints for the Next.js frontend.
# Exists to ensure duplicated auth/profile routes inside api_v3 behave as expected without relying on legacy URLs.

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from users.factories import UserFactory

pytestmark = pytest.mark.django_db


def test_api_v3_login_returns_tokens():
    password = "Supersafe123!"
    user = UserFactory(password=password)
    client = APIClient()

    url = reverse("v3-token-obtain-pair")
    response = client.post(url, {"email": user.email, "password": password}, format="json")

    assert response.status_code == 200
    body = response.json()
    assert "access" in body
    assert "refresh" in body


def test_api_v3_current_user_requires_authentication():
    client = APIClient()
    url = reverse("v3-current-user")

    response = client.get(url, format="json")

    assert response.status_code == 401


def test_api_v3_current_user_returns_profile():
    user = UserFactory(email="frontend-user@example.com", first_name="Front", last_name="End")
    client = APIClient()
    client.force_authenticate(user=user)

    url = reverse("v3-current-user")
    response = client.get(url, format="json")

    assert response.status_code == 200
    body = response.json()
    assert body["email"] == user.email
    assert body["first_name"] == user.first_name
    assert body["last_name"] == user.last_name
