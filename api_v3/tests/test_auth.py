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
