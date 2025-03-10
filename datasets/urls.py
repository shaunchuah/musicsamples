from django.urls import path

from datasets.views import (
    DatasetAnalyticsCreateUpdateView,
    DatasetCreateUpdateView,
    DataSourceStatusCheckView,
    RetrieveDatasetAPIView,
    dataset_access_history,
    dataset_export_csv,
    list_datasets,
)

app_name = "datasets"
urlpatterns = [
    path("api/create/", DatasetCreateUpdateView.as_view(), name="create"),
    path("api/retrieve/<str:name>/", RetrieveDatasetAPIView.as_view(), name="retrieve"),
    path("api/status_check/", DataSourceStatusCheckView.as_view(), name="status_check"),
    path("api/analytics/", DatasetAnalyticsCreateUpdateView.as_view(), name="analytics"),
    path("list/", list_datasets, name="list"),
    path("export_csv/<str:dataset_name>/", dataset_export_csv, name="export_csv"),
    path("access_history/<str:dataset_name>/", dataset_access_history, name="access_history"),
]
