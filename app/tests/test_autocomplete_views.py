import json

from django.test import Client, TestCase
from django.urls import reverse

from app.factories import SampleFactory
from users.factories import UserFactory


class TestAutocomplete(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client = Client()
        self.client.force_login(self.user, backend=None)

    def test_autocomplete_locations(self):
        SampleFactory(sample_location="location1")
        SampleFactory(sample_location="test2")
        path = reverse("autocomplete_locations")
        response = self.client.get(path + "?term=loc")
        assert "location1" in json.loads(response.content)
        assert "test2" not in json.loads(response.content)

        response_2 = self.client.get(path + "?term=te")
        assert "location1" not in json.loads(response_2.content)
        assert "test2" in json.loads(response_2.content)

        response_3 = self.client.get(path)
        assert "location1" in json.loads(response_3.content)
        assert "test2" in json.loads(response_3.content)

    def test_autocomplete_patient_id(self):
        SampleFactory(patient_id="GID-123-P")
        SampleFactory(patient_id="GID-003-P")
        path = reverse("autocomplete_patients")
        response = self.client.get(path + "?term=GID-123")
        assert "GID-123-P" in json.loads(response.content)
        assert "GID-003-P" not in json.loads(response.content)

        response_2 = self.client.get(path + "?term=003")
        assert "GID-123-P" not in json.loads(response_2.content)
        assert "GID-003-P" in json.loads(response_2.content)

        response_3 = self.client.get(path)
        assert "GID-123-P" in json.loads(response_3.content)
        assert "GID-003-P" in json.loads(response_3.content)
