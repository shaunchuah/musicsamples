from django.db import models
from django.contrib.auth.models import User
from simple_history.models import HistoricalRecords
from ckeditor_uploader.fields import RichTextUploadingField
from taggit.managers import TaggableManager


class Sample(models.Model):
    sample_id = models.CharField(max_length=200, unique=True)
    patientid = models.CharField(max_length=200)
    sample_location = models.CharField(max_length=200)
    sample_type = models.CharField(max_length=200)
    sample_datetime = models.DateTimeField()
    sample_comments = models.TextField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    processing_datetime = models.DateTimeField(blank=True, null=True)
    sample_volume = models.DecimalField(
        max_digits=10, decimal_places=3, blank=True, null=True
    )
    sample_volume_units = models.CharField(max_length=30, blank=True, null=True)
    freeze_thaw_count = models.IntegerField(default=0)

    sample_sublocation = models.CharField(max_length=200, blank=True, null=True)
    is_fully_used = models.BooleanField(default=False)

    haemolysis_reference = models.CharField(max_length=200, blank=True, null=True)
    biopsy_location = models.CharField(max_length=100, blank=True, null=True)
    biopsy_inflamed_status = models.CharField(max_length=100, blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=200)
    last_modified = models.DateTimeField(auto_now=True)
    last_modified_by = models.CharField(max_length=200)

    history = HistoricalRecords()

    def clean(self):
        self.sample_id = self.sample_id.upper()
        self.patientid = self.patientid.upper()

    def __str__(self):
        return self.sample_id


class Note(models.Model):
    title = models.CharField(max_length=200, unique=True)
    content = RichTextUploadingField(blank=True, null=True)
    sample_tags = models.ManyToManyField(Sample, blank=True)
    is_public = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    tags = TaggableManager(blank=True)

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notes")
    published_date = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    class Meta:
        ordering = ["-published_date"]

    def __str__(self):
        return self.title
