from django.urls import resolve, reverse

from app import views


DATASTORE_VIEW_CASES = [
    ("datastore:list", {}, views.datastore_list_view),
    ("datastore:create", {}, views.datastore_create_view),
    ("datastore:create_ajax", {}, views.datastore_create_view_ajax),
    ("datastore:download", {"id": 1}, views.datastore_download_view),
    ("datastore:azure_view", {"id": 1}, views.datastore_azure_view),
    ("datastore:detail", {"id": 1}, views.datastore_detail_view),
    ("datastore:edit", {"id": 1}, views.datastore_edit_metadata_view),
    ("datastore:delete", {"id": 1}, views.datastore_delete_view),
    ("datastore:search", {}, views.datastore_search_view),
    ("datastore:search_export_csv", {}, views.datastore_search_export_csv),
    ("datastore:filter", {}, views.datastore_filter_view),
    ("datastore:filter_export_csv", {}, views.datastore_filter_export_csv),
]


def test_datastore_view_functions():
    for name, kwargs, view in DATASTORE_VIEW_CASES:
        resolved = resolve(reverse(name, kwargs=kwargs) if kwargs else reverse(name))
        assert resolved.func is view


def test_datastore_api_endpoints():
    for name, url_name in [
        ("datastore:file_direct_upload_start", "file_direct_upload_start"),
        ("datastore:file_direct_upload_finish", "file_direct_upload_finish"),
        ("datastore:import_study_identifiers", "import_study_identifiers"),
        ("datastore:import_clinical_data", "import_clinical_data"),
    ]:
        resolved = resolve(reverse(name))
        assert resolved.url_name == url_name
        assert resolved.namespace == "datastore"
