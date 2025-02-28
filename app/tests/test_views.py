import pytest
from django.test import Client, TestCase
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed

from app.factories import SampleFactory, StudyIdentifierFactory
from app.models import Sample
from users.factories import UserFactory

pytestmark = pytest.mark.django_db


@pytest.fixture
def test_password():
    return "strong-test-pass"


@pytest.fixture
def create_user(db, django_user_model, test_password):
    def make_user(**kwargs):
        kwargs["password"] = test_password
        if "email" not in kwargs:
            kwargs["email"] = "testuser1@test.com"
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


def test_add_sample_page(auto_login_user):
    client, user = auto_login_user()
    path = reverse("sample_add")
    response = client.get(path)
    assert response.status_code == 200, "Should return add new sample page via GET request."
    response = client.post(path)
    assert response.status_code == 200, "Should return add new sample page via POST request without form data."


def test_add_sample_post(auto_login_user):
    client, user = auto_login_user()
    path = reverse("sample_add")
    form_data = {
        "study_name": "gidamps",
        "sample_id": "test001",
        "study_id": "patient001",
        "sample_location": "location001",
        "sample_type": "cfdna_plasma",
        "sample_datetime": "2020-01-01T13:20:30",
        "sample_comments": "",
        "processing_datetime": "2020-01-01T13:20:30",
        "sample_sublocation": "",
        "sample_volume": "",
        "sample_volume_units": "",
        "freeze_thaw_count": 0,
        "haemolysis_reference": "",
        "biopsy_location": "",
        "biopsy_inflamed_status": "",
    }
    response = client.post(path, data=form_data)
    assert Sample.objects.get(pk=1).study_id.name == "PATIENT001"  # should return study_id as uppercase as well
    assert response.status_code == 302


def test_sample_detail_page(auto_login_user):
    client, user = auto_login_user()
    SampleFactory(sample_id="TEST001")
    path = reverse("sample_detail", kwargs={"pk": 1})
    response = client.get(path)
    assert (
        response.context["sample"].sample_id == "TEST001"
    ), "Should create sample with ID TEST001 and retrieve sample detail view."


def test_sample_detail_processing_datetime_logic(auto_login_user):
    client, user = auto_login_user()
    SampleFactory(
        sample_datetime="2020-01-01T13:20:30+00",
        processing_datetime="2020-01-01T13:25:30+00",
    )
    path = reverse("sample_detail", kwargs={"pk": 1})
    response = client.get(path)
    assert (
        response.context["processing_time"] == 5
    ), "Should test processing_time calculation given sampling and processing datetime."


def test_sample_edit_page(auto_login_user):
    client, user = auto_login_user()
    SampleFactory(sample_id="TEST002")
    SampleFactory(sample_id="TEST003")
    path = reverse("sample_edit", kwargs={"pk": 2})
    response = client.get(path)
    assertTemplateUsed(response, "samples/sample-add.html")
    assert (
        response.context["form"].initial["sample_id"] == "TEST003"
    ), "Should create two separate sample instances and return the second one."


def test_sample_search_page(auto_login_user):
    client, user = auto_login_user()
    SampleFactory(sample_id="TEST002")
    SampleFactory(sample_id="TEST003")
    SampleFactory(sample_id="NO")
    SampleFactory(sample_id="DONOTRETURN")
    path = reverse("sample_search")
    response = client.get(path + "?q=TEST")

    assert (
        response.context["sample_list"].count() == 2
    ), "Should create a few objects, run a search and return 2 objects."

    response = client.get(path)
    assert response.context["query_string"] == "Null", "Should return no objects with empty query string."


def test_sample_checkout_page(auto_login_user):
    client, user = auto_login_user()
    SampleFactory(sample_location="location1")
    path = reverse("sample_checkout", kwargs={"pk": 1})

    # Get the sample checkout page and check template is correct
    response = client.get(path)
    assert (
        response.context["form"].initial["sample_location"] == "location1"
    ), "Should retrieve an instance to checkout."

    # Checkout the sample from location1 to location2
    response = client.post(path, data={"sample_location": "location2"})
    assert (
        Sample.objects.get(pk=1).sample_location == "location2"
    ), "Should checkout the sample location from location1 to location2."
    assert Sample.objects.get(pk=1).last_modified_by == "testuser1@test.com"
    assert response.status_code == 302


def test_sample_used(auto_login_user):
    client, user = auto_login_user()
    SampleFactory()
    path = reverse("sample_used", kwargs={"pk": 1})

    # Get the delete page first and check template is correct
    response = client.get(path)
    assertTemplateUsed(response, "samples/sample-used.html")

    # Make the delete request now and also pass a next_url to check redirection
    response = client.post(path, data={"is_used": True})

    assert Sample.objects.get(pk=1).is_used is True, "Should delete the created sample"
    assert response.status_code == 302


def test_sample_reactivate(auto_login_user):
    client, user = auto_login_user()
    SampleFactory(is_used=True)
    path = reverse("reactivate_sample", kwargs={"pk": 1})

    # Get the restore page and check template is correct
    response = client.get(path)
    assertTemplateUsed(response, "samples/sample-reactivate.html")

    # Restore the sample
    response = client.post(path, data={"is_used": False})
    assert Sample.objects.get(pk=1).is_used is False, "Should restore the deleted sample"
    assert response.url == "/"


def test_export_csv_view(auto_login_user):
    client, user = auto_login_user()
    path = reverse("export_csv", kwargs={"study_name": "gidamps"})
    response = client.get(path)
    assert response.status_code == 200
    assert response["Content-Type"] == "text/csv"
    assert "attachment" in response["Content-Disposition"]


def test_filter_view(auto_login_user):
    client, user = auto_login_user()
    SampleFactory(study_id=StudyIdentifierFactory(name="GID-123-P"))
    path = reverse("filter")
    response = client.get(path + "?study_id__name=gid-123-P")
    assert response.status_code == 200
    assert response.context["sample_filter"].qs.all()[0].study_id.name == "GID-123-P"


class TestViews(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client = Client()
        self.client.force_login(self.user, backend=None)
        self.anonymous_client = Client()

    def test_add_sample_page(self):
        url = reverse("sample_add")
        response = self.client.get(url)
        assert response.status_code == 200, "Should return add new sample page via GET request."

    def test_add_marvel_sample(self):
        url = reverse("sample_add")
        form_data = {
            "study_name": "marvel",
            "music_timepoint": "",
            "marvel_timepoint": "baseline",
            "sample_id": "test001",
            "study_id": "patient001",
            "sample_location": "location001",
            "sample_type": "cfdna_plasma",
            "sample_datetime": "2020-01-01T13:20:30",
            "sample_comments": "",
            "processing_datetime": "2020-01-01T13:20:30",
            "sample_sublocation": "",
            "sample_volume": "",
            "sample_volume_units": "",
            "freeze_thaw_count": 0,
            "haemolysis_reference": "",
            "biopsy_location": "",
            "biopsy_inflamed_status": "",
        }
        self.client.post(url, data=form_data)
        created_sample = Sample.objects.get(sample_id="TEST001")
        assert created_sample.study_name == "marvel"
        assert created_sample.frozen_datetime is None

    def test_add_non_marvel_sample(self):
        url = reverse("sample_add")
        form_data = {
            "study_name": "music",
            "music_timepoint": "baseline",
            "marvel_timepoint": "",
            "sample_id": "test001",
            "study_id": "patient001",
            "sample_location": "location001",
            "sample_type": "cfdna_plasma",
            "sample_datetime": "2020-01-01T13:20:30",
            "sample_comments": "",
            "processing_datetime": "2020-01-01T13:20:30",
            "sample_sublocation": "",
            "sample_volume": "",
            "sample_volume_units": "",
            "freeze_thaw_count": 0,
            "haemolysis_reference": "",
            "biopsy_location": "",
            "biopsy_inflamed_status": "",
        }
        self.client.post(url, data=form_data)
        created_sample = Sample.objects.get(sample_id="TEST001")
        assert created_sample.study_name != "marvel"

    def test_add_marvel_sample_with_frozen_datetime(self):
        url = reverse("sample_add")
        form_data = {
            "study_name": "marvel",
            "marvel_timepoint": "12_weeks",
            "sample_id": "test001",
            "study_id": "patient001",
            "sample_location": "location001",
            "sample_type": "cfdna_plasma",
            "sample_datetime": "2020-01-01T13:20:30",
            "sample_comments": "",
            "processing_datetime": "2020-01-01T13:20:30",
            "frozen_datetime": "2020-01-01T16:20:00",
            "sample_sublocation": "",
            "sample_volume": "",
            "sample_volume_units": "",
            "freeze_thaw_count": 0,
            "haemolysis_reference": "",
            "biopsy_location": "",
            "biopsy_inflamed_status": "",
        }
        self.client.post(url, data=form_data)
        created_sample = Sample.objects.get(sample_id="TEST001")
        assert created_sample.frozen_datetime is not None

    def test_add_sample_unique(self):
        SampleFactory(sample_id="TEST001")
        url = reverse("sample_add")
        form_data = {
            "study_name": "marvel",
            "marvel_timepoint": "12_weeks",
            "sample_id": "test001",
            "study_id": "patient001",
            "sample_location": "location001",
            "sample_type": "cfdna_plasma",
            "sample_datetime": "2020-01-01T13:20:30",
            "sample_comments": "",
            "processing_datetime": "2020-01-01T13:20:30",
            "frozen_datetime": "2020-01-01T16:20:00",
            "sample_sublocation": "",
            "sample_volume": "",
            "sample_volume_units": "",
            "freeze_thaw_count": 0,
            "haemolysis_reference": "",
            "biopsy_location": "",
            "biopsy_inflamed_status": "",
        }
        response = self.client.post(url, data=form_data)
        assert response.context["form"].errors["sample_id"][0] == "Sample with this Sample id already exists."
        created_sample = Sample.objects.get(sample_id="TEST001")
        assert created_sample.study_id != "patient001"
