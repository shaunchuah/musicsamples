from django.urls import path

from .. import views

urlpatterns = [
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
]
