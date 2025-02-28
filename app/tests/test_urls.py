from django.test import SimpleTestCase
from django.urls import resolve, reverse

from app import views


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
        url = reverse("datastore_list")
        self.assertEqual(resolve(url).func, views.datastore_list_view)

    def test_datastore_create_url_resolves(self):
        url = reverse("datastore_create")
        self.assertEqual(resolve(url).func, views.datastore_create_view)

    def test_datastore_create_ajax_url_resolves(self):
        url = reverse("datastore_create_ajax")
        self.assertEqual(resolve(url).func, views.datastore_create_view_ajax)

    def test_datastore_download_url_resolves(self):
        url = reverse("datastore_download", kwargs={"id": 1})
        self.assertEqual(resolve(url).func, views.datastore_download_view)

    def test_datastore_azure_view_url_resolves(self):
        url = reverse("datastore_azure_view", kwargs={"id": 1})
        self.assertEqual(resolve(url).func, views.datastore_azure_view)

    def test_datastore_detail_url_resolves(self):
        url = reverse("datastore_detail", kwargs={"id": 1})
        self.assertEqual(resolve(url).func, views.datastore_detail_view)

    def test_datastore_edit_url_resolves(self):
        url = reverse("datastore_edit", kwargs={"id": 1})
        self.assertEqual(resolve(url).func, views.datastore_edit_metadata_view)

    def test_datastore_delete_url_resolves(self):
        url = reverse("datastore_delete", kwargs={"id": 1})
        self.assertEqual(resolve(url).func, views.datastore_delete_view)

    def test_datastore_search_url_resolves(self):
        url = reverse("datastore_search")
        self.assertEqual(resolve(url).func, views.datastore_search_view)

    def test_datastore_search_export_csv_url_resolves(self):
        url = reverse("datastore_search_export_csv")
        self.assertEqual(resolve(url).func, views.datastore_search_export_csv)

    def test_datastore_filter_url_resolves(self):
        url = reverse("datastore_filter")
        self.assertEqual(resolve(url).func, views.datastore_filter_view)

    def test_datastore_filter_export_csv_url_resolves(self):
        url = reverse("datastore_filter_export_csv")
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
