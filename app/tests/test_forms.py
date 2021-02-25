import pytest
from .. import forms

pytestmark = pytest.mark.django_db

class TestSampleForm:
    def test_empty_form(self):
        form = forms.SampleForm(data={})
        assert form.is_valid() is False, 'Form should be invalid if no data provided'

