from mixer.backend.django import mixer
import pytest

pytestmark = pytest.mark.django_db


class TestSample:
    def test_model(self):
        obj = mixer.blend("app.Sample")
        assert obj.pk == 1, "Should create sample instance with primary key id of 1."


class TestNote:
    def test_note_model(self):
        note = mixer.blend("app.Note")
        assert note.pk == 1, "Should create a new note with primary key id of 1."


def test_return_sample_id():
    sample = mixer.blend("app.Sample", sample_id="test001")
    assert sample.__str__() == "test001"


def test_sample_model_cleaning():
    sample = mixer.blend("app.Sample", sample_id="test001")
    sample.clean()
    assert sample.sample_id == "TEST001"


def test_sample_cleaning_and_returning():
    sample = mixer.blend("app.Sample", sample_id="test002")
    sample.clean()
    assert sample.__str__() == "TEST002"


def test_note_returns_title():
    note = mixer.blend("app.Note", title="Test Title")
    assert note.__str__() == "Test Title"
