from django.test import SimpleTestCase
from django.urls import resolve, reverse

from app import views
from app.views.box_views import (
    ExperimentalIdCreateView,
    ExperimentalIdDeleteView,
    ExperimentalIdDetailView,
    ExperimentalIdListView,
    ExperimentalIdRestoreView,
    ExperimentalIdUpdateView,
    box_filter,
    box_filter_export_csv,
    box_search,
    create_experimental_id,
    experiment_filter,
    experiment_search,
    experimental_id_filter_export_csv,
    export_boxes_csv,
    export_experiments_csv,
)
from datasets.views import (
    dataset_access_history,
    dataset_export_csv,
    list_datasets,
)
from users.views import (
    activate_account_view,
    deactivate_account_view,
    delete_token,
    edit_profile_view,
    edit_user_view,
    generate_token,
    login_view,
    make_staff_view,
    new_user_view,
    refresh_token,
    remove_staff_view,
    user_list_view,
)


class TestUrls(SimpleTestCase):
    def test_index_url_resolves(self):
        url = reverse("home")
        self.assertEqual(resolve(url).func, views.index)

    def test_analytics_url_resolves(self):
        url = reverse("analytics")
        self.assertEqual(resolve(url).func, views.analytics)

    def test_mini_music_analytics_url_resolves(self):
        url = reverse("sample_types_pivot", kwargs={"study_name": "mini_music"})
        self.assertEqual(resolve(url).func, views.sample_types_pivot)

    def test_reference_url_resolves(self):
        url = reverse("reference")
        self.assertEqual(resolve(url).func, views.reference)

    def test_add_sample_url_resolves(self):
        url = reverse("sample_add")
        self.assertEqual(resolve(url).func, views.sample_add)

    def test_view_single_sample_url_resolves(self):
        url = reverse("sample_detail", kwargs={"pk": 1})
        self.assertEqual(resolve(url).func, views.sample_detail)

    def test_edit_sample_url_resolves(self):
        url = reverse("sample_edit", kwargs={"pk": 23})
        self.assertEqual(resolve(url).func, views.sample_edit)

    def test_checkout_sample_url_resolves(self):
        url = reverse("sample_checkout", kwargs={"pk": 3})
        self.assertEqual(resolve(url).func, views.sample_checkout)

    def test_search_url_resolves(self):
        url = reverse("sample_search")
        self.assertEqual(resolve(url).func, views.sample_search)

    def test_export_csv_url_resolves(self):
        url = reverse("export_csv", kwargs={"study_name": "all"})
        self.assertEqual(resolve(url).func, views.export_csv_view)

    def test_account_page_url_resolves(self):
        url = reverse("account")
        self.assertEqual(resolve(url).func, views.account)

    def test_autocomplete_locations_url_resolves(self):
        url = reverse("autocomplete_locations")
        self.assertEqual(resolve(url).func, views.autocomplete_locations)

    def test_autocomplete_sublocations_url_resolves(self):
        url = reverse("autocomplete_sublocations")
        self.assertEqual(resolve(url).func, views.autocomplete_sublocations)

    def test_autocomplete_study_id_url_resolves(self):
        url = reverse("autocomplete_patients")
        self.assertEqual(resolve(url).func, views.autocomplete_study_id)

    def test_barcode_url_resolves(self):
        url = reverse("barcode")
        self.assertEqual(resolve(url).func, views.barcode)

    def test_barcode_samples_used_url_resolves(self):
        url = reverse("barcode_samples_used")
        self.assertEqual(resolve(url).func, views.barcode_samples_used)

    def test_barcode_add_multiple_url_resolves(self):
        url = reverse("barcode_add_multiple")
        self.assertEqual(resolve(url).func, views.barcode_add_multiple)

    def test_data_export_url_resolves(self):
        url = reverse("data_export")
        self.assertEqual(resolve(url).func, views.data_export)

    def test_filter_url(self):
        url = reverse("filter")
        self.assertEqual(resolve(url).func, views.filter)

    def test_filter_export_csv_url(self):
        url = reverse("filter_export_csv")
        self.assertEqual(resolve(url).func, views.filter_export_csv)

    def test_used_samples_url_resolves(self):
        url = reverse("used_samples")
        self.assertEqual(resolve(url).func, views.used_samples)

    def test_used_samples_search_url_resolves(self):
        url = reverse("used_samples_search")
        self.assertEqual(resolve(url).func, views.used_samples_search)

    def test_used_samples_archive_all_url_resolves(self):
        url = reverse("used_samples_archive_all")
        self.assertEqual(resolve(url).func, views.used_samples_archive_all)

    def test_sample_used_url_resolves(self):
        url = reverse("sample_used", kwargs={"pk": 1})
        self.assertEqual(resolve(url).func, views.sample_used)

    def test_reactivate_sample_url_resolves(self):
        url = reverse("reactivate_sample", kwargs={"pk": 1})
        self.assertEqual(resolve(url).func, views.reactivate_sample)

    def test_no_timepoint_view_url_resolves(self):
        url = reverse("no_timepoint_view", kwargs={"study_name": "music"})
        self.assertEqual(resolve(url).func, views.no_timepoint_view)

    # DataStore URLs
    def test_datastore_list_url_resolves(self):
        url = reverse("datastore:list")
        self.assertEqual(resolve(url).func, views.datastore_list_view)

    def test_datastore_create_url_resolves(self):
        url = reverse("datastore:create")
        self.assertEqual(resolve(url).func, views.datastore_create_view)

    def test_datastore_create_ajax_url_resolves(self):
        url = reverse("datastore:create_ajax")
        self.assertEqual(resolve(url).func, views.datastore_create_view_ajax)

    def test_datastore_download_url_resolves(self):
        url = reverse("datastore:download", kwargs={"id": 1})
        self.assertEqual(resolve(url).func, views.datastore_download_view)

    def test_datastore_azure_view_url_resolves(self):
        url = reverse("datastore:azure_view", kwargs={"id": 1})
        self.assertEqual(resolve(url).func, views.datastore_azure_view)

    def test_datastore_detail_url_resolves(self):
        url = reverse("datastore:detail", kwargs={"id": 1})
        self.assertEqual(resolve(url).func, views.datastore_detail_view)

    def test_datastore_edit_url_resolves(self):
        url = reverse("datastore:edit", kwargs={"id": 1})
        self.assertEqual(resolve(url).func, views.datastore_edit_metadata_view)

    def test_datastore_delete_url_resolves(self):
        url = reverse("datastore:delete", kwargs={"id": 1})
        self.assertEqual(resolve(url).func, views.datastore_delete_view)

    def test_datastore_search_url_resolves(self):
        url = reverse("datastore:search")
        self.assertEqual(resolve(url).func, views.datastore_search_view)

    def test_datastore_search_export_csv_url_resolves(self):
        url = reverse("datastore:search_export_csv")
        self.assertEqual(resolve(url).func, views.datastore_search_export_csv)

    def test_datastore_filter_url_resolves(self):
        url = reverse("datastore:filter")
        self.assertEqual(resolve(url).func, views.datastore_filter_view)

    def test_datastore_filter_export_csv_url_resolves(self):
        url = reverse("datastore:filter_export_csv")
        self.assertEqual(resolve(url).func, views.datastore_filter_export_csv)

    # Export related URLs
    def test_export_users_url_resolves(self):
        url = reverse("export_users")
        self.assertEqual(resolve(url).func, views.export_users)

    def test_export_samples_url_resolves(self):
        url = reverse("export_samples")
        self.assertEqual(resolve(url).func, views.export_samples)

    def test_export_historical_samples_url_resolves(self):
        url = reverse("export_historical_samples")
        self.assertEqual(resolve(url).func, views.export_historical_samples)

    # Management URL
    def test_management_url_resolves(self):
        url = reverse("management")
        self.assertEqual(resolve(url).func, views.management)

    # API v2 URLs
    def test_api_v2_login_url_resolves(self):
        url = "/api/v2/auth/login/"
        self.assertEqual(resolve(url).func, views.login_view)

    def test_api_v2_token_refresh_url_resolves(self):
        url = reverse("token_refresh")
        resolved = resolve(url)
        self.assertEqual(resolved.url_name, "token_refresh")

    def test_api_v2_token_verify_url_resolves(self):
        url = reverse("token_verify")
        resolved = resolve(url)
        self.assertEqual(resolved.url_name, "token_verify")

    # Study ID URLs
    def test_study_id_list_url_resolves(self):
        url = reverse("study_id_list")
        self.assertEqual(resolve(url).func, views.study_id_list_view)

    def test_study_id_edit_url_resolves(self):
        url = reverse("study_id_edit", kwargs={"name": "test"})
        self.assertEqual(resolve(url).func, views.study_id_edit_view)

    def test_study_id_search_url_resolves(self):
        url = reverse("study_id_search")
        self.assertEqual(resolve(url).func, views.study_id_search_view)

    def test_study_id_delete_url_resolves(self):
        url = reverse("study_id_delete", kwargs={"id": 1})
        self.assertEqual(resolve(url).func, views.study_id_delete_view)

    def test_study_id_detail_url_resolves(self):
        url = reverse("study_id_detail", kwargs={"name": "test"})
        self.assertEqual(resolve(url).func, views.study_id_detail_view)

    # Datastore API URLs
    def test_datastore_file_direct_upload_start_url_resolves(self):
        url = reverse("datastore:file_direct_upload_start")
        resolved = resolve(url)
        self.assertEqual(resolved.url_name, "file_direct_upload_start")

    def test_datastore_file_direct_upload_finish_url_resolves(self):
        url = reverse("datastore:file_direct_upload_finish")
        resolved = resolve(url)
        self.assertEqual(resolved.url_name, "file_direct_upload_finish")

    def test_datastore_import_study_identifiers_url_resolves(self):
        url = reverse("datastore:import_study_identifiers")
        self.assertEqual(resolve(url).func, views.import_study_identifiers)

    def test_datastore_import_clinical_data_url_resolves(self):
        url = reverse("datastore:import_clinical_data")
        self.assertEqual(resolve(url).func, views.import_clinical_data)


class TestBoxUrls(SimpleTestCase):
    def test_box_list_url_resolves(self):
        url = reverse("boxes:list")
        resolved = resolve(url)
        self.assertEqual(resolved.url_name, "list")
        self.assertEqual(resolved.namespace, "boxes")

    def test_box_filter_url_resolves(self):
        url = reverse("boxes:filter")
        self.assertEqual(resolve(url).func, box_filter)

    def test_box_filter_export_csv_url_resolves(self):
        url = reverse("boxes:filter_export_csv")
        self.assertEqual(resolve(url).func, box_filter_export_csv)

    def test_box_create_url_resolves(self):
        url = reverse("boxes:create")
        resolved = resolve(url)
        self.assertEqual(resolved.url_name, "create")
        self.assertEqual(resolved.namespace, "boxes")

    def test_box_detail_url_resolves(self):
        url = reverse("boxes:detail", kwargs={"pk": 1})
        resolved = resolve(url)
        self.assertEqual(resolved.url_name, "detail")
        self.assertEqual(resolved.namespace, "boxes")

    def test_box_edit_url_resolves(self):
        url = reverse("boxes:edit", kwargs={"pk": 1})
        resolved = resolve(url)
        self.assertEqual(resolved.url_name, "edit")
        self.assertEqual(resolved.namespace, "boxes")

    def test_box_delete_url_resolves(self):
        url = reverse("boxes:delete", kwargs={"pk": 1})
        resolved = resolve(url)
        self.assertEqual(resolved.url_name, "delete")
        self.assertEqual(resolved.namespace, "boxes")

    def test_box_search_url_resolves(self):
        url = reverse("boxes:search")
        self.assertEqual(resolve(url).func, box_search)

    def test_box_export_csv_url_resolves(self):
        url = reverse("boxes:export_csv")
        self.assertEqual(resolve(url).func, export_boxes_csv)

    def test_box_create_experimental_id_url_resolves(self):
        url = reverse("boxes:create_experimental_id")
        self.assertEqual(resolve(url).func, create_experimental_id)

    def test_experimental_id_list_url_resolves(self):
        url = reverse("boxes:experimental_id_list")
        resolved = resolve(url)
        self.assertEqual(resolved.func.view_class, ExperimentalIdListView)  # type: ignore
        self.assertEqual(resolved.url_name, "experimental_id_list")
        self.assertEqual(resolved.namespace, "boxes")

    def test_experimental_id_create_url_resolves(self):
        url = reverse("boxes:experimental_id_create")
        resolved = resolve(url)
        self.assertEqual(resolved.func.view_class, ExperimentalIdCreateView)  # type: ignore
        self.assertEqual(resolved.url_name, "experimental_id_create")
        self.assertEqual(resolved.namespace, "boxes")

    def test_experimental_id_detail_url_resolves(self):
        url = reverse("boxes:experimental_id_detail", kwargs={"pk": 1})
        resolved = resolve(url)
        self.assertEqual(resolved.func.view_class, ExperimentalIdDetailView)  # type: ignore
        self.assertEqual(resolved.url_name, "experimental_id_detail")
        self.assertEqual(resolved.namespace, "boxes")

    def test_experimental_id_edit_url_resolves(self):
        url = reverse("boxes:experimental_id_edit", kwargs={"pk": 1})
        resolved = resolve(url)
        self.assertEqual(resolved.func.view_class, ExperimentalIdUpdateView)  # type: ignore
        self.assertEqual(resolved.url_name, "experimental_id_edit")
        self.assertEqual(resolved.namespace, "boxes")

    def test_experimental_id_delete_url_resolves(self):
        url = reverse("boxes:experimental_id_delete", kwargs={"pk": 1})
        resolved = resolve(url)
        self.assertEqual(resolved.func.view_class, ExperimentalIdDeleteView)  # type: ignore
        self.assertEqual(resolved.url_name, "experimental_id_delete")
        self.assertEqual(resolved.namespace, "boxes")

    def test_experimental_id_restore_url_resolves(self):
        url = reverse("boxes:experimental_id_restore", kwargs={"pk": 1})
        resolved = resolve(url)
        self.assertEqual(resolved.func.view_class, ExperimentalIdRestoreView)  # type: ignore
        self.assertEqual(resolved.url_name, "experimental_id_restore")
        self.assertEqual(resolved.namespace, "boxes")

    def test_experimental_id_search_url_resolves(self):
        url = reverse("boxes:experimental_id_search")
        self.assertEqual(resolve(url).func, experiment_search)

    def test_experimental_id_export_csv_url_resolves(self):
        url = reverse("boxes:experimental_id_export_csv")
        self.assertEqual(resolve(url).func, export_experiments_csv)

    def test_experimental_id_filter_url_resolves(self):
        url = reverse("boxes:experimental_id_filter")
        self.assertEqual(resolve(url).func, experiment_filter)

    def test_experimental_id_filter_export_csv_url_resolves(self):
        url = reverse("boxes:experimental_id_filter_export_csv")
        self.assertEqual(resolve(url).func, experimental_id_filter_export_csv)


class TestDatasetUrls(SimpleTestCase):
    def test_dataset_create_url_resolves(self):
        url = reverse("datasets:create")
        resolved = resolve(url)
        self.assertEqual(resolved.url_name, "create")
        self.assertEqual(resolved.namespace, "datasets")

    def test_dataset_retrieve_url_resolves(self):
        url = reverse("datasets:retrieve", kwargs={"name": "test"})
        resolved = resolve(url)
        self.assertEqual(resolved.url_name, "retrieve")
        self.assertEqual(resolved.namespace, "datasets")

    def test_dataset_status_check_url_resolves(self):
        url = reverse("datasets:status_check")
        resolved = resolve(url)
        self.assertEqual(resolved.url_name, "status_check")
        self.assertEqual(resolved.namespace, "datasets")

    def test_dataset_analytics_url_resolves(self):
        url = reverse("datasets:analytics")
        resolved = resolve(url)
        self.assertEqual(resolved.url_name, "analytics")
        self.assertEqual(resolved.namespace, "datasets")

    def test_dataset_list_url_resolves(self):
        url = reverse("datasets:list")
        self.assertEqual(resolve(url).func, list_datasets)

    def test_dataset_export_csv_url_resolves(self):
        url = reverse("datasets:export_csv", kwargs={"dataset_name": "test"})
        self.assertEqual(resolve(url).func, dataset_export_csv)

    def test_dataset_access_history_url_resolves(self):
        url = reverse("datasets:access_history", kwargs={"dataset_name": "test"})
        self.assertEqual(resolve(url).func, dataset_access_history)


class TestUserUrls(SimpleTestCase):
    def test_user_login_url_resolves(self):
        url = reverse("login")
        self.assertEqual(resolve(url).func, login_view)

    def test_user_logout_url_resolves(self):
        url = reverse("logout")
        resolved = resolve(url)
        self.assertEqual(resolved.url_name, "logout")

    def test_user_password_reset_done_url_resolves(self):
        url = reverse("password_reset_done")
        resolved = resolve(url)
        self.assertEqual(resolved.url_name, "password_reset_done")

    def test_user_password_reset_confirm_url_resolves(self):
        url = reverse("password_reset_confirm", kwargs={"uidb64": "test", "token": "test"})
        resolved = resolve(url)
        self.assertEqual(resolved.url_name, "password_reset_confirm")

    def test_user_password_reset_complete_url_resolves(self):
        url = reverse("password_reset_complete")
        resolved = resolve(url)
        self.assertEqual(resolved.url_name, "password_reset_complete")

    def test_user_password_reset_url_resolves(self):
        url = reverse("password_reset")
        resolved = resolve(url)
        self.assertEqual(resolved.url_name, "password_reset")

    def test_user_password_change_url_resolves(self):
        url = reverse("password_change")
        resolved = resolve(url)
        self.assertEqual(resolved.url_name, "password_change")

    def test_user_password_change_done_url_resolves(self):
        url = reverse("password_change_done")
        resolved = resolve(url)
        self.assertEqual(resolved.url_name, "password_change_done")

    def test_user_obtain_auth_token_url_resolves(self):
        url = reverse("obtain_auth_token")
        resolved = resolve(url)
        self.assertEqual(resolved.url_name, "obtain_auth_token")

    def test_user_generate_token_url_resolves(self):
        url = reverse("generate_token")
        self.assertEqual(resolve(url).func, generate_token)

    def test_user_delete_token_url_resolves(self):
        url = reverse("delete_token")
        self.assertEqual(resolve(url).func, delete_token)

    def test_user_refresh_token_url_resolves(self):
        url = reverse("refresh_token")
        self.assertEqual(resolve(url).func, refresh_token)

    def test_user_new_user_url_resolves(self):
        url = reverse("new_user")
        self.assertEqual(resolve(url).func, new_user_view)

    def test_user_list_url_resolves(self):
        url = reverse("user_list")
        self.assertEqual(resolve(url).func, user_list_view)

    def test_user_make_staff_url_resolves(self):
        url = reverse("make_staff", kwargs={"user_id": 1})
        self.assertEqual(resolve(url).func, make_staff_view)

    def test_user_remove_staff_url_resolves(self):
        url = reverse("remove_staff", kwargs={"user_id": 1})
        self.assertEqual(resolve(url).func, remove_staff_view)

    def test_user_activate_account_url_resolves(self):
        url = reverse("activate_account", kwargs={"user_id": 1})
        self.assertEqual(resolve(url).func, activate_account_view)

    def test_user_deactivate_account_url_resolves(self):
        url = reverse("deactivate_account", kwargs={"user_id": 1})
        self.assertEqual(resolve(url).func, deactivate_account_view)

    def test_user_edit_user_url_resolves(self):
        url = reverse("edit_user", kwargs={"user_id": 1})
        self.assertEqual(resolve(url).func, edit_user_view)

    def test_user_edit_profile_url_resolves(self):
        url = reverse("edit_profile")
        self.assertEqual(resolve(url).func, edit_profile_view)
