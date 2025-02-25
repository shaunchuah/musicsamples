from django.test import Client, TestCase
from django.urls import reverse

from app.choices import StudyNameChoices
from app.factories import SampleFactory
from users.factories import UserFactory


class TestStudyFilters(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client = Client()
        self.client.force_login(self.user, backend=None)
        self.music_sample = SampleFactory(study_name=StudyNameChoices.MUSIC, study_id__name="MID-90-2")
        self.gidamps_sample = SampleFactory(study_name=StudyNameChoices.GIDAMPS, study_id__name="GID-203-P")
        self.mini_music_sample = SampleFactory(study_name=StudyNameChoices.MINI_MUSIC, study_id__name="MINI-166-3")
        self.marvel_sample = SampleFactory(study_name=StudyNameChoices.MARVEL, study_id__name="239105")

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
