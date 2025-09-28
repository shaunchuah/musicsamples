import pytest
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed

from app.factories import SampleFactory
from app.models import Sample

pytestmark = pytest.mark.django_db


def test_sample_checkout_page(auto_login_user):
    client, user = auto_login_user()
    SampleFactory(sample_location="location1")
    path = reverse("sample_checkout", kwargs={"pk": 1})

    response = client.get(path)
    assert response.context["form"].initial["sample_location"] == "location1"

    response = client.post(path, data={"sample_location": "location2"})

    sample = Sample.objects.get(pk=1)
    assert sample.sample_location == "location2"
    assert sample.last_modified_by == user.email
    assert response.status_code == 302


def test_sample_used(auto_login_user):
    client, _ = auto_login_user()
    SampleFactory()
    path = reverse("sample_used", kwargs={"pk": 1})

    response = client.get(path)
    assertTemplateUsed(response, "samples/sample-used.html")

    response = client.post(path, data={"is_used": True})

    assert Sample.objects.get(pk=1).is_used is True
    assert response.status_code == 302


def test_sample_reactivate(auto_login_user):
    client, _ = auto_login_user()
    SampleFactory(is_used=True)
    path = reverse("reactivate_sample", kwargs={"pk": 1})

    response = client.get(path)
    assertTemplateUsed(response, "samples/sample_reactivate.html")

    response = client.post(path, data={"is_used": False})

    assert Sample.objects.get(pk=1).is_used is False
    assert response.url == "/"
