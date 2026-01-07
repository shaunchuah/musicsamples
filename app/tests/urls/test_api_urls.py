from django.urls import resolve, reverse


def test_v3_token_refresh_url_name():
    resolved = resolve(reverse("v3-token-refresh"))
    assert resolved.url_name == "v3-token-refresh"
