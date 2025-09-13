from django.urls import path

from .. import views

app_name = "datastore"

urlpatterns = [
    path("dashboard/", views.datastore_list_view, name="list"),
    path("upload/", views.datastore_create_view, name="create"),
    path("upload/ajax/", views.datastore_create_view_ajax, name="create_ajax"),
    path("download/<int:id>/", views.datastore_download_view, name="download"),
    path("azure_view/<int:id>/", views.datastore_azure_view, name="azure_view"),
    path("read/<int:id>/", views.datastore_detail_view, name="detail"),
    path("edit/<int:id>/", views.datastore_edit_metadata_view, name="edit"),
    path("delete/<int:id>/", views.datastore_delete_view, name="delete"),
    path("search/", views.datastore_search_view, name="search"),
    path("search/export_csv/", views.datastore_search_export_csv, name="search_export_csv"),
    path("filter/", views.datastore_filter_view, name="filter"),
    path("filter/export_csv/", views.datastore_filter_export_csv, name="filter_export_csv"),
    path("api/upload/start/", views.FileDirectUploadStartApi.as_view(), name="file_direct_upload_start"),
    path("api/upload/finish/", views.FileDirectUploadFinishApi.as_view(), name="file_direct_upload_finish"),
    path("api/import_study_id/", views.import_study_identifiers, name="import_study_identifiers"),
    path("api/import_clinical_data/", views.import_clinical_data, name="import_clinical_data"),
]
