import pytest
from django.urls import reverse

from app.factories import BasicScienceBoxFactory
from users.factories import UserFactory


@pytest.fixture
def box_user():
    return UserFactory()


@pytest.fixture
def box_user_with_permission(box_user, grant_permission):
    return grant_permission(box_user, "view_basicsciencebox")


@pytest.fixture
def basic_science_box():
    return BasicScienceBoxFactory()


@pytest.fixture
def box_detail_url(basic_science_box):
    return reverse("boxes:detail", kwargs={"pk": basic_science_box.pk})


@pytest.fixture
def box_list_url():
    return reverse("boxes:list")
