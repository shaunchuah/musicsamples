import pytest

from users.factories import UserFactory


@pytest.fixture
def test_password():
    return "strong-test-pass"


@pytest.fixture
def create_user(db, django_user_model, test_password):
    def make_user(**kwargs):
        kwargs.setdefault("email", "testuser1@test.com")
        kwargs.setdefault("password", test_password)
        return django_user_model.objects.create_user(**kwargs)

    return make_user


@pytest.fixture
def other_user(db, django_user_model):
    return django_user_model.objects.create(email="user2@test.com", password="user2")


@pytest.fixture
def auto_login_user(db, client, create_user, test_password):
    def make_auto_login(user=None):
        if user is None:
            user = create_user()
        client.login(username=user.email, password=test_password)
        return client, user

    return make_auto_login


@pytest.fixture
def sample_client(client):
    user = UserFactory()
    client.force_login(user)
    return client, user
