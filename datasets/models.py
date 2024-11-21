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
