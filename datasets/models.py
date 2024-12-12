from django.conf import settings
from django.db import models

from app.choices import StudyNameChoices


class Dataset(models.Model):
    # Fields for API loading
    study_name = models.CharField(max_length=200, choices=StudyNameChoices.choices)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    json = models.JSONField(blank=True, null=True)

    # Metadata
    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class DatasetAnalytics(models.Model):
    name = models.CharField(max_length=255, unique=True)
    data = models.JSONField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class DatasetAccessTypeChoices(models.TextChoices):
    CSV = "CSV", "CSV"
    JSON = "JSON", "JSON"
    NOT_RECORDED = "NR", "Not Recorded"


class DatasetAccessHistory(models.Model):
    """
    Takes in dataset, user and access_type as input.
    Access type can be either CSV or JSON.
    """

    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    access_type = models.CharField(
        max_length=50, choices=DatasetAccessTypeChoices.choices, default=DatasetAccessTypeChoices.NOT_RECORDED
    )
    accessed = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} accessed {self.dataset} on {self.accessed.strftime('%Y-%m-%d %H:%M:%S')}"


class DataSourceStatusCheck(models.Model):
    data_source = models.CharField(max_length=255)  # could be API server or S3 file
    response_status = models.IntegerField()
    error_message = models.TextField(blank=True, null=True)
    checked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"API check for {self.data_source} at {self.checked_at.strftime('%Y-%m-%d %H:%M:%S')}"
