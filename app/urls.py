from django.urls import path, include
from app import views
from rest_framework import routers
from .views import (
    SampleViewSet,
    SampleIsFullyUsedViewSet,
    MultipleSampleViewSet,
    SampleExportViewset,
)
from django.views.generic.base import TemplateView

router = routers.DefaultRouter()

# Django Rest Framework API endpoints
router.register(r"samples", SampleViewSet, "samples")
router.register(r"samples_used", SampleIsFullyUsedViewSet, "samples_used")
router.register(r"multiple_samples", MultipleSampleViewSet, "multiple_samples")
router.register(r"gidamps", SampleExportViewset, "gidamps")

urlpatterns = [
    path("", views.index, name="home"),
    path(
        "robots.txt",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
    ),
    path("analytics/", views.analytics, name="analytics"),
    path("analytics/gid_overview", views.gid_overview, name="gid_overview"),
    path("reference/", views.reference, name="reference"),
    path("account/", views.account, name="account"),
    path("data_export/", views.data_export, name="data_export"),
    # Samples URLs
    path("samples/archive/", views.sample_archive, name="sample_archive"),
    path("used_samples/", views.used_samples, name="used_samples"),
    path("used_samples/search/", views.used_samples_search, name="used_samples_search"),
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
    # path('export_csv/', views.export_csv, name='export_csv'),
    path("export_excel/", views.export_excel, name="export_excel"),
    # Notes URLs
    path("notes/", views.notes, name="notes"),
    path("notes/<int:pk>/", views.note_detail, name="note_detail"),
    path("notes/add/", views.note_add, name="note_add"),
    path("notes/<int:pk>/edit/", views.note_edit, name="note_edit"),
    path("notes/<int:pk>/delete/", views.note_delete, name="note_delete"),
    path("notes/personal/", views.note_personal, name="note_personal"),
    path("notes/tag/<slug>", views.note_tags, name="note_tags"),
    path("notes/authors/<int:pk>", views.note_authors, name="note_authors"),
    path("notes/search/", views.note_search, name="note_search"),
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
    path("autocomplete/tags/", views.autocomplete_tags, name="autocomplete_tags"),
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
