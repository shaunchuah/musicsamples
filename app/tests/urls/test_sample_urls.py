from django.urls import resolve, reverse

from app import views


SAMPLE_URL_CASES = [
    ("sample_add", {}, views.sample_add),
    ("sample_detail", {"pk": 1}, views.sample_detail),
    ("sample_edit", {"pk": 1}, views.sample_edit),
    ("sample_checkout", {"pk": 1}, views.sample_checkout),
    ("sample_search", {}, views.sample_search),
    ("export_csv", {"study_name": "all"}, views.export_csv_view),
    ("filter", {}, views.filter),
    ("filter_export_csv", {}, views.filter_export_csv),
    ("used_samples", {}, views.used_samples),
    ("used_samples_search", {}, views.used_samples_search),
    ("used_samples_archive_all", {}, views.used_samples_archive_all),
    ("sample_used", {"pk": 1}, views.sample_used),
    ("reactivate_sample", {"pk": 1}, views.reactivate_sample),
    ("no_timepoint_view", {"study_name": "music"}, views.no_timepoint_view),
    ("autocomplete_locations", {}, views.autocomplete_locations),
    ("autocomplete_sublocations", {}, views.autocomplete_sublocations),
    ("autocomplete_patients", {}, views.autocomplete_study_id),
    ("barcode", {}, views.barcode),
    ("barcode_samples_used", {}, views.barcode_samples_used),
    ("barcode_add_multiple", {}, views.barcode_add_multiple),
]


def test_sample_urls_resolve_to_expected_views():
    for name, kwargs, view in SAMPLE_URL_CASES:
        resolved = resolve(reverse(name, kwargs=kwargs) if kwargs else reverse(name))
        assert resolved.func is view
