from django.contrib import admin

from datasets.models import Dataset, DatasetAccessHistory, DatasetAnalytics, DataSourceStatusCheck


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ["name", "description", "study_name", "created", "last_modified"]


@admin.register(DatasetAccessHistory)
class DatasetAccessHistoryAdmin(admin.ModelAdmin):
    list_display = ["user", "dataset", "accessed", "access_type"]


@admin.register(DataSourceStatusCheck)
class DataSourceStatusCheckAdmin(admin.ModelAdmin):
    list_display = ["data_source", "response_status", "error_message", "checked_at"]


@admin.register(DatasetAnalytics)
class DatasetAnalyticsAdmin(admin.ModelAdmin):
    list_display = ["name", "created", "last_modified"]
