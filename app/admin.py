from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from app.models import DataStore, Sample


@admin.register(Sample)
class SampleAdmin(SimpleHistoryAdmin):
    list_display = [
        "sample_id",
        "study_name",
        "patient_id",
        "sample_location",
        "sample_sublocation",
        "sample_comments",
    ]


@admin.register(DataStore)
class DataStoreAdmin(admin.ModelAdmin):
    list_display = ["study_name", "category", "original_file_name", "file_type", "upload_finished_at", "uploaded_by"]
