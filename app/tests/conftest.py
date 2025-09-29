import pytest


@pytest.fixture
def grant_permission():
    """Return a callable that attaches the named permission to a user."""

    def _grant(user, codename: str, app_label: str = "app", *, name: str | None = None):
        permission_model = user.user_permissions.model
        permission, _ = permission_model.objects.get_or_create(
            codename=codename,
            content_type__app_label=app_label,
            defaults={"name": name or codename.replace("_", " ").title()},
        )
        user.user_permissions.add(permission)
        return user

    return _grant
