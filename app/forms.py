from django import forms
from django.utils import timezone
from django.forms import ModelForm, modelformset_factory, formset_factory
from .models import Sample, Note
from ckeditor_uploader.widgets import CKEditorUploadingWidget

class DateTimeInput(forms.DateTimeInput):
    input_type = "datetime-local"

    def __init__(self, **kwargs):
        kwargs["format"] = "%Y-%m-%dT%H:%M"
        super().__init__(**kwargs)

def currentTime():
    time = timezone.localtime(timezone.now())
    return time

class SampleForm(ModelForm):
    sample_datetime = forms.DateTimeField(label="Sample Created Datetime*", widget=DateTimeInput(), initial=currentTime)
    class Meta:
        model = Sample
        fields = ['musicsampleid', 'sample_location', 'patientid', 'sample_type', 'sample_datetime', 'sample_comments', 'processing_datetime', 'sample_sublocation', 'sample_volume', 'sample_volume_units', 'freeze_thaw_count', 'haemolysis_reference', ]
        HAEMOLYSIS_REFERENCE_CHOICES = (
            ('', 'Select category'),
            ('0', 'Minimal'),
            ('20', '20 mg/dL'),
            ('50', '50 mg/dL'),
            ('100', '100 mg/dL (unusable)'),
            ('250', '250 mg/dL (unusable)'),
            ('500', '500 mg/dL (unusable)'),
            ('1000', '1000 mg/dL (unusable)'),
        )
        SAMPLE_VOLUME_UNIT_CHOICES = (
            ('', 'Select unit'),
            ('ml', 'ml'),
            ('ul', 'ul'),
        )
        SAMPLE_TYPE_CHOICES = (
            ('', 'Select type'),
            ('Standard EDTA tube',(
                ('Standard EDTA tube', 'Standard EDTA tube'),
                ('EDTA plasma child aliquot', 'EDTA plasma child aliquot'),
            )),
            ('PaxGene ccfDNA tube',(
                ('PaxGene ccfDNA tube', 'PaxGene ccfDNA tube'),
                ('PaxGene ccfDNA plasma child aliquot', 'PaxGene ccfDNA plasma child aliquot'),
                ('PaxGene ccfDNA extracted cfDNA', 'PaxGene ccfDNA extracted cfDNA'),
            )),
            ('PaxGene RNA tube', (
                ('PaxGene RNA tube', 'PaxGene RNA tube'),
                ('PaxGene RNA child aliquot', 'PaxGene RNA child aliquot'),
            )),
            ('Standard Gel/Serum tube', (
                ('Standard gel tube', 'Standard gel tube'),
                ('Serum child aliquot', 'Serum child aliquot'),
            )),
            ('Tissue/Biopsy', (
                ('Formalin biopsy', 'Formalin biopsy'),
                ('RNAlater biopsy', 'RNAlater biopsy'),
                ('Paraffin tissue block', 'Paraffin tissue block'),
            )),
            ('Stool', (
                ('Calprotectin', 'Calprotectin'),
                ('FIT', 'FIT'),
                ('OmniGut', 'Omnigut'),
                ('Stool supernatant', 'Stool supernatant'),
            )),
            ('Saliva', (
                ('Saliva', 'Saliva'),
            )),
            ('Other', (
                ('Other', 'Other please specify in comments'),
            )),
        )
        widgets = {
            'sample_type': forms.Select(choices=SAMPLE_TYPE_CHOICES),
            'sample_volume_units': forms.Select(choices=SAMPLE_VOLUME_UNIT_CHOICES, attrs={'class': 'form-control'}),
            'processing_datetime': DateTimeInput(),
            'haemolysis_reference': forms.Select(choices=HAEMOLYSIS_REFERENCE_CHOICES),
        }
        labels = {
            'musicsampleid': "Sample ID*",
            'patientid': "Patient ID*",
            'sample_location': "Sample Location*",
            'sample_sublocation': "Sample Sublocation",
            'sample_type': "Sample Type*",
            'sample_comments': "Comments",
            'processing_datetime': "Processing Datetime",
            'sample_volume': "Volume Remaining (est.)",
            'sample_volume_units': "Sample Volume Units",
            'freeze_thaw_count': "No. of Freeze-Thaw Cycles",
            'haemolysis_reference': "Haemolysis Reference Palette"
        }

class CheckoutForm(ModelForm):
    class Meta:
        model = Sample
        fields = ['sample_location', 'sample_sublocation']
        labels = { 'sample_location': "Sample Location", 'sample_sublocation': "Sample Sublocation",}

class DeleteForm(ModelForm):
    class Meta:
        model = Sample
        fields = ['is_deleted']
        labels = { 'is_deleted': "Confirm delete?" }

class RestoreForm(ModelForm):
    class Meta:
        model = Sample
        fields = ['is_deleted']
        labels = { 'is_deleted': "Uncheck to restore" }

class FullyUsedForm(ModelForm):
    class Meta:
        model = Sample
        fields = ['is_fully_used']
        labels = { 'is_fully_used': "Mark sample as fully used?" }

class ReactivateForm(ModelForm):
    class Meta:
        model = Sample
        fields = ['is_fully_used']
        labels = { 'is_fully_used': "Uncheck to reactivate" }

#SampleFormSet = modelformset_factory(Sample, fields=('musicsampleid', 'patientid', 'sample_location', 'sample_type', 'sample_datetime', 'sample_comments'), extra=2)
SampleFormSet = formset_factory(SampleForm, extra=1)

class NoteForm(ModelForm):   
    class Meta:
        model = Note
        fields = ['title', 'content', 'sample_tags', 'is_public']
        widgets = {
            'content': forms.CharField(widget=CKEditorUploadingWidget())
        }
        
class NoteDeleteForm(ModelForm):
    class Meta:
        model = Note
        fields = ['is_deleted']
        labels = { 'is_deleted': "Confirm delete?" }