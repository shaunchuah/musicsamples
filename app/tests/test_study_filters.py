from django.test import Client, TestCase
from django.urls import reverse

from app.choices import StudyNameChoices
from app.factories import SampleFactory
from authentication.factories import UserFactory


class TestStudyFilters(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client = Client()
        self.client.force_login(self.user, backend=None)
        self.music_sample = SampleFactory(
            study_name=StudyNameChoices.MUSIC, patient_id="MID-90-2"
        )
        self.gidamps_sample = SampleFactory(
            study_name=StudyNameChoices.GIDAMPS, patient_id="GID-203-P"
        )
        self.mini_music_sample = SampleFactory(
            study_name=StudyNameChoices.MINI_MUSIC, patient_id="MINI-166-3"
        )
        self.marvel_sample = SampleFactory(
            study_name=StudyNameChoices.MARVEL, patient_id="239105"
        )

    def test_gidamps_study_filter(self):
        path = reverse("filter") + "?study_name=gidamps"
        response = self.client.get(path)
        content = response.content.decode()
        assert self.music_sample.sample_id not in content
        assert self.gidamps_sample.sample_id in content
        assert self.mini_music_sample.sample_id not in content
        assert self.marvel_sample.sample_id not in content

    def test_music_study_filter(self):
        path = reverse("filter") + "?study_name=music"
        response = self.client.get(path)
        content = response.content.decode()
        assert self.music_sample.sample_id in content
        assert self.gidamps_sample.sample_id not in content
        assert self.mini_music_sample.sample_id not in content
        assert self.marvel_sample.sample_id not in content

    def test_mini_music_study_filter(self):
        path = reverse("filter") + "?study_name=mini_music"
        response = self.client.get(path)
        content = response.content.decode()
        assert self.music_sample.sample_id not in content
        assert self.gidamps_sample.sample_id not in content
        assert self.mini_music_sample.sample_id in content
        assert self.marvel_sample.sample_id not in content

    def test_marvel_study_filter(self):
        path = reverse("filter") + "?study_name=marvel"
        response = self.client.get(path)
        content = response.content.decode()
        assert self.music_sample.sample_id not in content
        assert self.gidamps_sample.sample_id not in content
        assert self.mini_music_sample.sample_id not in content
        assert self.marvel_sample.sample_id in content
