# api_v3/tests/test_auth_and_users.py
# Covers api_v3 authentication and user profile endpoints for the Next.js frontend.
# Exists to ensure duplicated auth/profile routes inside api_v3 behave as expected without relying on legacy URLs.

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from app.factories import SampleFactory
from users.factories import UserFactory

User = get_user_model()

pytestmark = pytest.mark.django_db


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


def test_api_v3_current_user_patch_updates_profile():
    user = UserFactory(email="edit-me@example.com", first_name="Old")
    client = APIClient()
    client.force_authenticate(user=user)

    url = reverse("v3-current-user")
    response = client.patch(url, {"first_name": "NewName"}, format="json")

    assert response.status_code == 200
    user.refresh_from_db()
    assert user.first_name == "NewName"


def test_password_reset_request_rejects_invalid_email():
    client = APIClient()
    url = reverse("v3-password-reset")

    response = client.post(url, {"email": ""}, format="json")

    assert response.status_code == 400
    assert "error" in response.json()


def test_password_change_updates_password():
    user = UserFactory(email="changer@example.com")
    client = APIClient()
    client.force_authenticate(user=user)

    url = reverse("v3-password-change")
    response = client.post(url, {"new_password": "A-secure-pass-123"}, format="json")

    assert response.status_code == 200
    user.refresh_from_db()
    assert user.check_password("A-secure-pass-123")


def test_staff_user_create_and_welcome_email(settings, mailoutbox):
    staff_user = UserFactory(is_staff=True)
    client = APIClient()
    client.force_authenticate(user=staff_user)

    url = reverse("v3-users-list")
    response = client.post(
        url,
        {"email": "newuser@example.com", "first_name": "New", "last_name": "User"},
        format="json",
    )

    assert response.status_code == 201
    assert mailoutbox  # welcome email sent


def test_staff_user_create_requires_email():
    staff_user = UserFactory(is_staff=True)
    client = APIClient()
    client.force_authenticate(user=staff_user)

    url = reverse("v3-users-list")
    response = client.post(url, {"first_name": "New", "last_name": "User"}, format="json")

    assert response.status_code == 400
    assert "email" in response.json()


def test_staff_cannot_remove_own_staff_status():
    staff_user = UserFactory(is_staff=True)
    client = APIClient()
    client.force_authenticate(user=staff_user)

    url = reverse("v3-users-remove-staff", args=[staff_user.id])
    response = client.post(url, format="json")

    assert response.status_code == 400
    assert "error" in response.json()


def test_token_refresh_creates_new_token():
    user = UserFactory(email="token@example.com")
    client = APIClient()
    client.force_authenticate(user=user)

    create_url = reverse("v3-current-user-token")
    first = client.post(create_url, format="json").json()["token"]

    refresh_url = reverse("v3-current-user-token-refresh")
    refreshed = client.post(refresh_url, format="json").json()["token"]

    assert refreshed
    assert refreshed != first


def test_token_obtain_updates_last_login():
    user = UserFactory(email="login-last-login@example.com")
    assert user.last_login is None
    client = APIClient()
    url = reverse("v3-token-obtain-pair")
    response = client.post(
        url,
        {"email": user.email, "password": "testing_password"},
        format="json",
    )

    assert response.status_code == 200
    user.refresh_from_db()
    assert user.last_login is not None


def test_recent_samples_returns_only_user_samples():
    user = UserFactory(email="sampler@example.com")
    client = APIClient()
    client.force_authenticate(user=user)
    # create >20 to ensure cap
    for _ in range(25):
        SampleFactory(last_modified_by=user.email)
    SampleFactory(sample_id="OTHER-ID-123", last_modified_by="other@example.com")

    url = reverse("v3-current-user-recent-samples")
    response = client.get(url, format="json")

    assert response.status_code == 200
    body = response.json()
    assert body["count"] == 25  # only this user's samples count
    results = body["results"]
    assert len(results) == 20  # default page size
    sample_ids = [sample["sample_id"] for sample in results]
    assert "OTHER-ID-123" not in sample_ids


def test_management_user_emails_requires_staff():
    user = UserFactory()
    staff = UserFactory(is_staff=True)
    anonymous_email = "AnonymousUser"
    if not User.objects.filter(email=anonymous_email).exists():
        UserFactory(email=anonymous_email)
    client = APIClient()

    url = reverse("v3-management-user-emails")

    client.force_authenticate(user=user)
    assert client.get(url, format="json").status_code == 403

    client.force_authenticate(user=staff)
    response = client.get(url, format="json")
    assert response.status_code == 200
    body = response.json()
    assert "emails_joined" in body
    assert anonymous_email not in body["emails"]
    assert anonymous_email not in body["emails_joined"]


def test_staff_user_list_includes_activity_fields():
    staff = UserFactory(is_staff=True)
    target = UserFactory(last_login=timezone.now())

    client = APIClient()
    client.force_authenticate(user=staff)

    url = reverse("v3-users-list")
    response = client.get(url, format="json")

    assert response.status_code == 200
    body = response.json()
    users = body if isinstance(body, list) else body.get("results", [])
    matching = next(user for user in users if user["email"] == target.email)
    assert "last_login" in matching
    assert "date_joined" in matching
    assert "groups" in matching


def test_staff_user_rejects_invalid_choices():
    staff_user = UserFactory(is_staff=True)
    client = APIClient()
    client.force_authenticate(user=staff_user)

    url = reverse("v3-users-list")
    response = client.post(
        url,
        {
            "email": "badchoice@example.com",
            "first_name": "Bad",
            "last_name": "Choice",
            "job_title": "not-a-choice",
        },
        format="json",
    )

    assert response.status_code == 400
    body = response.json()
    assert "job_title" in body


def test_staff_user_patch_updates_groups():
    staff_user = UserFactory(is_staff=True)
    target_user = UserFactory()
    group_a = Group.objects.create(name="Admins")
    group_b = Group.objects.create(name="Editors")

    client = APIClient()
    client.force_authenticate(user=staff_user)

    url = reverse("v3-users-detail", args=[target_user.id])
    response = client.patch(
        url,
        {"groups": [group_a.name, group_b.name]},
        format="json",
    )

    assert response.status_code == 200
    target_user.refresh_from_db()
    assert set(target_user.groups.values_list("name", flat=True)) == {group_a.name, group_b.name}


def test_staff_user_groups_action_lists_available_groups():
    staff_user = UserFactory(is_staff=True)
    Group.objects.create(name="Admins")
    Group.objects.create(name="Editors")

    client = APIClient()
    client.force_authenticate(user=staff_user)

    url = reverse("v3-users-groups")
    response = client.get(url, format="json")

    assert response.status_code == 200
    body = response.json()
    assert set(body.get("groups", [])) == {"Admins", "Editors"}
