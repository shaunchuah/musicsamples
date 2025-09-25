import pytest
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed

from app.factories import SampleFactory

pytestmark = pytest.mark.django_db


def test_sample_edit_page(auto_login_user):
    client, _ = auto_login_user()
    SampleFactory(sample_id="TEST002")
    SampleFactory(sample_id="TEST003")

    response = client.get(reverse("sample_edit", kwargs={"pk": 2}))

    assertTemplateUsed(response, "samples/sample-add.html")
    assert response.context["form"].initial["sample_id"] == "TEST003"
