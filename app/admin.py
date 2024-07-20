from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from app.models import Sample


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
