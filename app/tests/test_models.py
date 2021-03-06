from mixer.backend.django import mixer
import pytest

pytestmark = pytest.mark.django_db


class TestSample:
    def test_model(self):
        obj = mixer.blend('app.Sample')
        assert obj.pk == 1, 'Should create sample instance with primary key id of 1.'


class TestNote:
    def test_note_model(self):
        note = mixer.blend('app.Note')
        assert note.pk == 1, 'Should create a new note with primary key id of 1.'
