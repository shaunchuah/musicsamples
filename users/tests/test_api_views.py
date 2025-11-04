# users/tests/test_api_views.py
# Exercises DRF user API endpoints to guarantee they expose profile data for the dashboard.
# Exists to prevent regressions when fetching the current user's identity and access metadata.

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework.test import APIClient


User = get_user_model()


@pytest.mark.django_db
def test_current_user_api_returns_profile_metadata():
    user = User.objects.create_user(  # type: ignore[arg-type]
        email="member@example.com",
        password="password123",
        first_name="Casey",
        last_name="North",
        is_staff=True,
    )
    group = Group.objects.create(name="researchers")
    user.groups.add(group)

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.get(reverse("current_user_api"))
    assert response.status_code == 200

    payload = response.json()
    assert payload["email"] == "member@example.com"
    assert payload["first_name"] == "Casey"
    assert payload["last_name"] == "North"
    assert payload["is_staff"] is True
    assert payload["is_superuser"] is False
    assert payload["groups"] == [group.name]


@pytest.mark.django_db
def test_current_user_api_requires_authentication():
    client = APIClient()
    response = client.get(reverse("current_user_api"))
    assert response.status_code == 401
    assert response.json()["detail"] in {"Authentication credentials were not provided.", "Unauthorized"}
