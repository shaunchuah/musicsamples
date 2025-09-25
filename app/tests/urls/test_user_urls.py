import pytest
from django.urls import resolve, reverse

from users.views import (
    activate_account_view,
    deactivate_account_view,
    delete_token,
    edit_profile_view,
    edit_user_view,
    generate_token,
    login_view,
    make_staff_view,
    new_user_view,
    refresh_token,
    remove_staff_view,
    user_list_view,
)


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("login", login_view),
        ("generate_token", generate_token),
        ("delete_token", delete_token),
        ("refresh_token", refresh_token),
        ("new_user", new_user_view),
        ("user_list", user_list_view),
        ("make_staff", make_staff_view),
        ("remove_staff", remove_staff_view),
        ("activate_account", activate_account_view),
        ("deactivate_account", deactivate_account_view),
        ("edit_user", edit_user_view),
        ("edit_profile", edit_profile_view),
    ],
)
def test_user_function_views(name, expected):
    kwargs = {"user_id": 1} if "user" in name and name not in {"user_list", "new_user"} else {}
    if name in {"make_staff", "remove_staff", "activate_account", "deactivate_account", "edit_user"}:
        kwargs = {"user_id": 1}
    resolved = resolve(reverse(name, kwargs=kwargs)) if kwargs else resolve(reverse(name))

    assert resolved.func is expected


@pytest.mark.parametrize(
    "name",
    [
        "logout",
        "password_reset_done",
        "password_reset_complete",
        "password_reset",
        "password_change",
        "password_change_done",
        "obtain_auth_token",
    ],
)
def test_user_named_urls(name):
    resolved = resolve(reverse(name))
    assert resolved.url_name == name


def test_password_reset_confirm_url():
    resolved = resolve(reverse("password_reset_confirm", kwargs={"uidb64": "test", "token": "test"}))
    assert resolved.url_name == "password_reset_confirm"
