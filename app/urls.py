from django.urls import include, path
from django.views.generic.base import TemplateView
from rest_framework import routers

from app import views

from .views import (
    AllSampleExportViewset,
    MultipleSampleViewSet,
    SampleExportViewset,
    SampleIsFullyUsedViewSet,
    SampleViewSet,
)

router = routers.DefaultRouter()

# Django Rest Framework API endpoints
router.register(r"samples", SampleViewSet, "samples")
router.register(r"samples_used", SampleIsFullyUsedViewSet, "samples_used")
router.register(r"multiple_samples", MultipleSampleViewSet, "multiple_samples")
router.register(r"gidamps", SampleExportViewset, "gidamps")
router.register(r"all", AllSampleExportViewset, "all")

urlpatterns = [
    path("", views.index, name="home"),
    # samples by study
    path(
        "filter/by_study/<str:study_name>/",
        views.filter_by_study,
        name="filter_by_study",
    ),
    path(
        "robots.txt",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
    ),
    path("filter/advance/<str:study_name>/", views.filter, name="filter"),
    path(
        "filter/export/<str:study_name>/",
        views.filter_export_csv,
        name="filter_export_csv",
    ),
    path("analytics/", views.analytics, name="analytics"),
    path(
        "analytics/minimusic_overview",
        views.minimusic_overview,
        name="minimusic_overview",
    ),
    path("reference/", views.reference, name="reference"),
    path("account/", views.account, name="account"),
    path("data_export/", views.data_export, name="data_export"),
    # Samples URLs
    path("samples/archive/", views.sample_archive, name="sample_archive"),
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
    path("samples/<int:pk>/delete/", views.sample_delete, name="sample_delete"),
    path("samples/<int:pk>/restore/", views.sample_restore, name="sample_restore"),
    path(
        "samples/<int:pk>/fully_used/",
        views.sample_fully_used,
        name="sample_fully_used",
    ),
    path(
        "samples/<int:pk>/reactivate_sample/",
        views.reactivate_sample,
        name="reactivate_sample",
    ),
    path("samples/<int:pk>/checkout/", views.sample_checkout, name="sample_checkout"),
    path("search/", views.sample_search, name="sample_search"),
    path(
        "export_csv/<str:study_name>/",
        views.export_study_samples,
        name="export_study_samples",
    ),
    path(
        "export_excel/<str:study_name>/", views.export_excel_view, name="export_excel"
    ),
    # Autocomplete API URLs
    path(
        "autocomplete/locations/",
        views.autocomplete_locations,
        name="autocomplete_locations",
    ),
    path(
        "autocomplete/patients/",
        views.autocomplete_patient_id,
        name="autocomplete_patients",
    ),
    # Django Rest Framework URLs
    path("api/", include(router.urls)),
    # QR code URLs
    path("barcode/", views.barcode, name="barcode"),
    path(
        "barcode/samples_used/", views.barcode_samples_used, name="barcode_samples_used"
    ),
    path(
        "barcode/add_multiple/", views.barcode_add_multiple, name="barcode_add_multiple"
    ),
]
