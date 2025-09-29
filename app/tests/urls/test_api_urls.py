from django.urls import resolve, reverse

from app import views


def test_api_v2_login_url_resolves():
    resolved = resolve("/api/v2/auth/login/")
    assert resolved.func is views.login_view


def test_token_refresh_url_name():
    resolved = resolve(reverse("token_refresh"))
    assert resolved.url_name == "token_refresh"


def test_token_verify_url_name():
    resolved = resolve(reverse("token_verify"))
    assert resolved.url_name == "token_verify"
