from django.contrib import admin

from datasets.models import Dataset, DatasetAccessHistory


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ["name", "description", "study_name", "created", "last_modified"]


@admin.register(DatasetAccessHistory)
class DatasetAccessHistoryAdmin(admin.ModelAdmin):
    list_display = ["user", "dataset", "accessed", "access_type"]
