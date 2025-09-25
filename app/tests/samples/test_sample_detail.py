import pytest
from django.urls import reverse

from app.factories import SampleFactory

pytestmark = pytest.mark.django_db


def test_sample_detail_page(auto_login_user):
    client, _ = auto_login_user()
    SampleFactory(sample_id="TEST001")

    response = client.get(reverse("sample_detail", kwargs={"pk": 1}))

    assert response.context["sample"].sample_id == "TEST001"


def test_sample_detail_processing_datetime_logic(auto_login_user):
    client, _ = auto_login_user()
    SampleFactory(
        sample_datetime="2020-01-01T13:20:30+00",
        processing_datetime="2020-01-01T13:25:30+00",
    )

    response = client.get(reverse("sample_detail", kwargs={"pk": 1}))

    assert response.context["processing_time"] == 5
