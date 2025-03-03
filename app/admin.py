from django.contrib import admin
from guardian.admin import GuardedModelAdmin
from simple_history.admin import SimpleHistoryAdmin

from app.models import DataStore, Sample, StudyIdentifier


@admin.register(StudyIdentifier)
class StudyIdentifierAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "study_name",
        "study_group",
        "study_center",
        "sex",
        "age",
    ]


@admin.register(Sample)
class SampleAdmin(SimpleHistoryAdmin):
    list_display = [
        "sample_id",
        "study_name",
        "study_id",
        "sample_location",
        "sample_sublocation",
        "sample_comments",
    ]


@admin.register(DataStore)
class DataStoreAdmin(GuardedModelAdmin):
    list_display = [
        "study_name",
        "category",
        "original_file_name",
        "formatted_file_name",
        "size",
        "file_type",
        "upload_finished_at",
        "uploaded_by",
        "comments",
        "music_timepoint",
        "marvel_timepoint",
    ]
