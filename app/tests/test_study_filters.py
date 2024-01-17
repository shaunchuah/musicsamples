from django.test import Client, TestCase
from django.urls import reverse

from app.factories import SampleFactory
from authentication.factories import UserFactory


class TestStudyFilters(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client = Client()
        self.client.force_login(self.user, backend=None)
        self.music_sample = SampleFactory(patient_id="MID-90-2")
        self.gidamps_sample = SampleFactory(patient_id="GID-203-P")
        self.mini_music_sample = SampleFactory(patient_id="MINI-166-3")
        self.marvel_sample = SampleFactory(patient_id="239105")

    def test_music_study_filter(self):
        path = reverse("filter_by_study", kwargs={"study_name": "music"})
        response = self.client.get(path)
        content = response.content.decode()
        assert self.music_sample.sample_id in content
        assert self.gidamps_sample.sample_id not in content
        assert self.mini_music_sample.sample_id not in content
        assert self.marvel_sample.sample_id not in content

    def test_gidamps_study_filter(self):
        path = reverse("filter_by_study", kwargs={"study_name": "gidamps"})
        response = self.client.get(path)
        content = response.content.decode()
        assert self.music_sample.sample_id not in content
        assert self.gidamps_sample.sample_id in content
        assert self.mini_music_sample.sample_id not in content
        assert self.marvel_sample.sample_id not in content

    def test_minimusic_study_filter(self):
        path = reverse("filter_by_study", kwargs={"study_name": "minimusic"})
        response = self.client.get(path)
        content = response.content.decode()
        assert self.music_sample.sample_id not in content
        assert self.gidamps_sample.sample_id not in content
        assert self.mini_music_sample.sample_id in content
        assert self.marvel_sample.sample_id not in content

    def test_marvel_study_filter(self):
        path = reverse("filter_by_study", kwargs={"study_name": "marvel"})
        response = self.client.get(path)
        content = response.content.decode()
        assert self.music_sample.sample_id not in content
        assert self.gidamps_sample.sample_id not in content
        assert self.mini_music_sample.sample_id not in content
        assert self.marvel_sample.sample_id in content
