import pytest
from .. import forms

pytestmark = pytest.mark.django_db

class TestSampleForm:
    def test_empty_form(self):
        form = forms.SampleForm(data={})
        assert form.is_valid() is False, 'Form should be invalid if no data provided'

sample_data = {
        'musicsampleid': 'sample001',
        'patientid': 'patient001',
        'sample_location': 'location1',
        'sample_type': 'PaxGene ccfDNA plasma child aliquot',
        'sample_datetime': '2021-01-01T11:00',
        'sample_comments': '',
        'processing_datetime': '',
        'sample_sublocation': '',
        'sample_volume': '',
        'sample_volume_units': '',
        'freeze_thaw_count': '',
        'haemolysis_reference': '', 
        'biopsy_location': '',
        'biopsy_inflamed_status': ''
    }