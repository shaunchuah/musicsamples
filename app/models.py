# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""

from django.db import models
from django.contrib.auth.models import User
from simple_history.models import HistoricalRecords

# Create your models here.
class Sample(models.Model):
    musicsampleid = models.CharField(max_length=200, unique=True)
    patientid = models.CharField(max_length=200)
    sample_location = models.CharField(max_length=200)
    sample_type = models.CharField(max_length=200)
    sample_datetime = models.DateTimeField()
    sample_comments = models.TextField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    processing_datetime = models.DateTimeField(blank=True, null=True)
    sample_volume = models.IntegerField(blank=True, null=True)
    sample_volume_units = models.CharField(max_length=30, blank=True, null=True)
    freeze_thaw_count = models.IntegerField(default=0)    
    
    created_by = models.CharField(max_length=200)
    last_modified_by = models.CharField(max_length=200)
    data_first_created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def clean(self):
        self.musicsampleid = self.musicsampleid.upper()
