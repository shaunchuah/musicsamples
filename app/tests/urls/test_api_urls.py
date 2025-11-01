from django.urls import resolve, reverse


def test_token_refresh_url_name():
    resolved = resolve(reverse("token_refresh"))
    assert resolved.url_name == "token_refresh"
