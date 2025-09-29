import pytest
from django.urls import reverse

from app.factories import SampleFactory, StudyIdentifierFactory

pytestmark = pytest.mark.django_db


def test_export_csv_view(auto_login_user):
    client, _ = auto_login_user()

    response = client.get(reverse("export_csv", kwargs={"study_name": "gidamps"}))

    assert response.status_code == 200
    assert response["Content-Type"] == "text/csv"
    assert "attachment" in response["Content-Disposition"]


def test_filter_view(auto_login_user):
    client, _ = auto_login_user()
    SampleFactory(study_id=StudyIdentifierFactory(name="GID-123-P"))

    response = client.get(reverse("filter") + "?study_id__name=gid-123-P")

    assert response.status_code == 200
    assert response.context["sample_filter"].qs.first().study_id.name == "GID-123-P"
