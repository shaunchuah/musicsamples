from django.urls import path

from .. import views

urlpatterns = [
    path("datastore/dashboard/", views.datastore_list_view, name="datastore_list"),
    path("datastore/upload/", views.datastore_create_view, name="datastore_create"),
    path("datastore/upload/ajax/", views.datastore_create_view_ajax, name="datastore_create_ajax"),
    path("datastore/download/<int:id>/", views.datastore_download_view, name="datastore_download"),
    path("datastore/azure_view/<int:id>/", views.datastore_azure_view, name="datastore_azure_view"),
    path("datastore/read/<int:id>/", views.datastore_detail_view, name="datastore_detail"),
    path("datastore/edit/<int:id>/", views.datastore_edit_metadata_view, name="datastore_edit"),
    path("datastore/delete/<int:id>/", views.datastore_delete_view, name="datastore_delete"),
    path("datastore/search/", views.datastore_search_view, name="datastore_search"),
    path("datastore/search/export_csv/", views.datastore_search_export_csv, name="datastore_search_export_csv"),
    path("datastore/filter/", views.datastore_filter_view, name="datastore_filter"),
    path("datastore/filter/export_csv/", views.datastore_filter_export_csv, name="datastore_filter_export_csv"),
    path("datastore/api/upload/start/", views.FileDirectUploadStartApi.as_view(), name="file_direct_upload_start"),
    path("datastore/api/upload/finish/", views.FileDirectUploadFinishApi.as_view(), name="file_direct_upload_finish"),
    path("datastore/api/import_study_id/", views.import_study_identifiers, name="import_study_identifiers"),
    path("datastore/api/import_clinical_data/", views.import_clinical_data, name="import_clinical_data"),
]
