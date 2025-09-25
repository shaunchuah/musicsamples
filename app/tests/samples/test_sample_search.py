import pytest
from django.urls import reverse

from app.factories import SampleFactory

pytestmark = pytest.mark.django_db


def test_sample_search_page(auto_login_user):
    client, _ = auto_login_user()
    SampleFactory(sample_id="TEST002")
    SampleFactory(sample_id="TEST003")
    SampleFactory(sample_id="NO")
    SampleFactory(sample_id="DONOTRETURN")

    response = client.get(reverse("sample_search") + "?q=TEST")
    assert response.context["sample_list"].count() == 2

    response = client.get(reverse("sample_search"))
    assert response.context["query_string"] == "Null"
