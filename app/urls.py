from django.urls import include, path
from django.views.generic.base import TemplateView
from rest_framework import routers
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from app import views

from .views import MultipleSampleViewSet, SampleIsUsedViewSet, SampleLocationViewSet, SampleV2ViewSet

router = routers.DefaultRouter()

# Django Rest Framework API endpoints
router.register(r"sample_location", SampleLocationViewSet, "sample_location")
router.register(r"samples_used", SampleIsUsedViewSet, "samples_used")
router.register(r"multiple_samples", MultipleSampleViewSet, "multiple_samples")

router_v2 = routers.DefaultRouter()
router_v2.register(r"samples", SampleV2ViewSet, "samples")

urlpatterns = [
    path("", views.index, name="home"),
    path(
        "robots.txt",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
    ),
    path("filter/", views.filter, name="filter"),
    path(
        "filter/export_csv/",
        views.filter_export_csv,
        name="filter_export_csv",
    ),
    path("analytics/", views.analytics, name="analytics"),
    path(
        "analytics/sample_types_pivot/<str:study_name>/",
        views.sample_types_pivot,
        name="sample_types_pivot",
    ),
    path("reference/", views.reference, name="reference"),
    path("account/", views.account, name="account"),
    path("data_export/", views.data_export, name="data_export"),
    path("management/", views.management, name="management"),
    # Samples URLs
    path("used_samples/", views.used_samples, name="used_samples"),
    path("used_samples/search/", views.used_samples_search, name="used_samples_search"),
    path(
        "used_samples/archive_all/",
        views.used_samples_archive_all,
        name="used_samples_archive_all",
    ),
    path("samples/add/", views.sample_add, name="sample_add"),
    path("samples/<int:pk>/", views.sample_detail, name="sample_detail"),
    path("samples/<int:pk>/edit/", views.sample_edit, name="sample_edit"),
    path(
        "samples/<int:pk>/used/",
        views.sample_used,
        name="sample_used",
    ),
    path(
        "samples/<int:pk>/reactivate_sample/",
        views.reactivate_sample,
        name="reactivate_sample",
    ),
    path("samples/<int:pk>/checkout/", views.sample_checkout, name="sample_checkout"),
    path("search/", views.sample_search, name="sample_search"),
    path("export_csv/<str:study_name>/", views.export_csv_view, name="export_csv"),
    # Autocomplete API URLs
    path(
        "autocomplete/locations/",
        views.autocomplete_locations,
        name="autocomplete_locations",
    ),
    path(
        "autocomplete/sublocations/",
        views.autocomplete_sublocations,
        name="autocomplete_sublocations",
    ),
    path(
        "autocomplete/patients/",
        views.autocomplete_study_id,
        name="autocomplete_patients",
    ),
    # Django Rest Framework URLs
    path("api/", include(router.urls)),
    # QR code URLs
    path("barcode/", views.barcode, name="barcode"),
    path("barcode/samples_used/", views.barcode_samples_used, name="barcode_samples_used"),
    path("barcode/add_multiple/", views.barcode_add_multiple, name="barcode_add_multiple"),
    path(
        "no_timepoint_view/<str:study_name>/",
        views.no_timepoint_view,
        name="no_timepoint_view",
    ),
    path("export_users/", views.export_users, name="export_users"),
    path("export_samples/", views.export_samples, name="export_samples"),
    path(
        "export_historical_samples/",
        views.export_historical_samples,
        name="export_historical_samples",
    ),
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
    path("study_id/", views.study_id_list_view, name="study_id_list"),
    path("study_id/edit/<str:name>/", views.study_id_edit_view, name="study_id_edit"),
    path("study_id/search/", views.study_id_search_view, name="study_id_search"),
    path("study_id/delete/<int:id>/", views.study_id_delete_view, name="study_id_delete"),
    path("study_id/detail/<str:name>/", views.study_id_detail_view, name="study_id_detail"),
    # Prototype API
    path("api/v2/auth/login/", views.login_view, name="login"),
    path("api/v2/auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/v2/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("api/v2/", include(router_v2.urls)),
]
