from django.contrib import admin

from datasets.models import Dataset


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ["name", "description", "study_name", "created", "last_modified"]
