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
        url = reverse("mini_music_overview")
        self.assertEqual(resolve(url).func, views.mini_music_overview)

    def test_reference_url_resolves(self):
        url = reverse("reference")
        self.assertEqual(resolve(url).func, views.reference)

    def test_archive_url_resolves(self):
        url = reverse("sample_archive")
        self.assertEqual(resolve(url).func, views.sample_archive)

    def test_add_sample_url_resolves(self):
        url = reverse("sample_add")
        self.assertEqual(resolve(url).func, views.sample_add)

    def test_view_single_sample_url_resolves(self):
        url = reverse("sample_detail", kwargs={"pk": 1})
        self.assertEqual(resolve(url).func, views.sample_detail)

    def test_edit_sample_url_resolves(self):
        url = reverse("sample_edit", kwargs={"pk": 23})
        self.assertEqual(resolve(url).func, views.sample_edit)

    def test_delete_sample_url_resolves(self):
        url = reverse("sample_delete", kwargs={"pk": 3})
        self.assertEqual(resolve(url).func, views.sample_delete)

    def test_restore_sample_url_resolves(self):
        url = reverse("sample_restore", kwargs={"pk": 3})
        self.assertEqual(resolve(url).func, views.sample_restore)

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

    def test_autocomplete_patient_id_url_resolves(self):
        url = reverse("autocomplete_patients")
        self.assertEqual(resolve(url).func, views.autocomplete_patient_id)

    def test_barcode_url_resolves(self):
        url = reverse("barcode")
        self.assertEqual(resolve(url).func, views.barcode)

    def test_barcode_samples_used_url_resolves(self):
        url = reverse("barcode_samples_used")
        self.assertEqual(resolve(url).func, views.barcode_samples_used)

    def test_data_export_url_resolves(self):
        url = reverse("data_export")
        self.assertEqual(resolve(url).func, views.data_export)

    def test_filter_url(self):
        url = reverse("filter", kwargs={"study_name": "all"})
        self.assertEqual(resolve(url).func, views.filter)

    def test_filter_export_csv_url(self):
        url = reverse("filter_export_csv", kwargs={"study_name": "all"})
        self.assertEqual(resolve(url).func, views.filter_export_csv)
