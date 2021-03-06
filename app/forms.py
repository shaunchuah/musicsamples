from django import forms
from django.utils import timezone
from django.forms import ModelForm
from .models import Sample, Note
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from taggit.forms import TagWidget
from django_select2.forms import ModelSelect2MultipleWidget


class DateTimeInput(forms.DateTimeInput):
    # Set default sample creation time to the time
    # the user is accessing the add new sample page
    input_type = "datetime-local"

    def __init__(self, **kwargs):
        kwargs["format"] = "%Y-%m-%dT%H:%M"
        super().__init__(**kwargs)


def currentTime():
    time = timezone.localtime(timezone.now())
    return time


class SampleForm(ModelForm):
    # Main sample registration form
    sample_datetime = forms.DateTimeField(
        label="Sample Created Datetime*",
        widget=DateTimeInput(),
        initial=currentTime
    )

    class Meta:
        model = Sample
        fields = [
            'musicsampleid',
            'sample_location',
            'patientid',
            'sample_type',
            'sample_datetime',
            'sample_comments',
            'processing_datetime',
            'sample_sublocation',
            'sample_volume',
            'sample_volume_units',
            'freeze_thaw_count',
            'haemolysis_reference',
            'biopsy_location',
            'biopsy_inflamed_status'
        ]

        # Customise dropdown select fields to ensure consistent data input
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
        BIOPSY_LOCATION_CHOICES = (
            ('', 'Select biopsy location'),
            ('Terminal ileum', 'Terminal ileum'),
            ('Caecum', 'Caecum'),
            ('Ascending colon', 'Ascending colon'),
            ('Transverse colon', 'Transverse colon'),
            ('Descending colon', 'Descending colon'),
            ('Sigmoid colon', 'Sigmoid colon'),
            ('Rectum', 'Rectum'),
            ('Right colon', 'Right colon'),
            ('Left colon', 'Left colon'),
        )
        BIOPSY_INFLAMED_STATUS_CHOICES = (
            ('', 'Select inflamed status'),
            ('inflamed', 'Inflamed'),
            ('uninflamed', 'Uninflamed'),
            ('healthy', 'Healthy'),
        )
        SAMPLE_VOLUME_UNIT_CHOICES = (
            ('', 'Select unit'),
            ('ml', 'ml'),
            ('ul', 'ul'),
        )
        SAMPLE_TYPE_CHOICES = (
            ('', 'Select type'),
            ('Standard EDTA tube', (
                ('Standard EDTA tube', 'Standard EDTA tube'),
                ('EDTA plasma child aliquot', 'EDTA plasma child aliquot'),
            )),
            ('PaxGene ccfDNA tube', (
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
            'biopsy_location': forms.Select(choices=BIOPSY_LOCATION_CHOICES),
            'biopsy_inflamed_status': forms.Select(choices=BIOPSY_INFLAMED_STATUS_CHOICES),
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
            'haemolysis_reference': "Haemolysis Reference Palette",
            'biopsy_location': "Biopsy Location",
            'biopsy_inflamed_status': "Biopsy Inflamed Status",
        }


class CheckoutForm(ModelForm):
    # Quick update of sample location from home page
    class Meta:
        model = Sample
        fields = ['sample_location', 'sample_sublocation']
        labels = {'sample_location': "Sample Location", 'sample_sublocation': "Sample Sublocation"}


class DeleteForm(ModelForm):
    # Soft deleting a sample
    class Meta:
        model = Sample
        fields = ['is_deleted']
        labels = {'is_deleted': "Confirm delete?"}


class RestoreForm(ModelForm):
    # Restoring a soft deleted sample
    class Meta:
        model = Sample
        fields = ['is_deleted']
        labels = {'is_deleted': "Uncheck to restore"}


class FullyUsedForm(ModelForm):
    # Marking a sample as fully used
    class Meta:
        model = Sample
        fields = ['is_fully_used']
        labels = {'is_fully_used': "Mark sample as fully used?"}


class ReactivateForm(ModelForm):
    # Restoring a sample that was accidentally marked as fully used
    class Meta:
        model = Sample
        fields = ['is_fully_used']
        labels = {'is_fully_used': "Uncheck to reactivate"}


#########################################################################
# NOTEFORMS  ############################################################
#########################################################################
# SELECT2 #####

# Create new note form
# Django select2 used to enable tagging of existing samples.
# Django taggit used for tagging of notes similar to blogging
# CKEditor Uploading widget used for adding of notes and supporting of file/image uploads - Suggest use an S3 backend to handle user media uploads.
# You can also disable this by switching the uploading widget for the standard one - see django-ckeditor documentation.

class NoteForm(ModelForm):
    class Meta:
        model = Note
        fields = ['title', 'content', 'sample_tags', 'tags', 'is_public']
        widgets = {
            'content': forms.CharField(widget=CKEditorUploadingWidget()),
            'tags': TagWidget(attrs={'data-role': 'tagsinput'}),

            'is_public': forms.Select(choices=((False, 'Private'), (True, 'Shared'))),
            'sample_tags': ModelSelect2MultipleWidget(
                model=Sample,
                search_fields=['musicsampleid__icontains']
            ),
        }
        labels = {
            'is_public': "Share settings:",
            'content': "",
        }


class NoteDeleteForm(ModelForm):
    # Soft deletion of notes. Restoration will probably have to be done
    # from the django admin panel unless you want to implement a restore
    # view similar to the above sample restoration methods.
    class Meta:
        model = Note
        fields = ['is_deleted']
        labels = {'is_deleted': "Confirm delete?"}
