import pytest
from .. import forms

pytestmark = pytest.mark.django_db


class TestSampleForm:
    def test_empty_form(self):
        form = forms.SampleForm(data={})
        assert form.is_valid() is False, 'Form should be invalid if no data provided'


def test_sample_add_form():
    sample_data = {
        'musicsampleid': 'test001',
        'patientid': 'patient001',
        'sample_location': 'location001',
        'sample_type': 'test_sample_type',
        'sample_datetime': '2020-01-01T13:20:30',
        'sample_comments': '',
        'processing_datetime': '2020-01-01T13:20:30',
        'sample_sublocation': '',
        'sample_volume': '',
        'sample_volume_units': '',
        'freeze_thaw_count': 0,
        'haemolysis_reference': '',
        'biopsy_location': '',
        'biopsy_inflamed_status': ''
    }
    form = forms.SampleForm(data=sample_data)
    assert form.is_valid() is True


def test_sample_add_form_without_processing_time():
    sample_data = {
        'musicsampleid': 'test001',
        'patientid': 'patient001',
        'sample_location': 'location001',
        'sample_type': 'test_sample_type',
        'sample_datetime': '2020-01-01T13:20:30',
        'sample_comments': '',
        'processing_datetime': '',
        'sample_sublocation': '',
        'sample_volume': '',
        'sample_volume_units': '',
        'freeze_thaw_count': 0,
        'haemolysis_reference': '',
        'biopsy_location': '',
        'biopsy_inflamed_status': ''
    }
    form = forms.SampleForm(data=sample_data)
    assert form.is_valid() is True