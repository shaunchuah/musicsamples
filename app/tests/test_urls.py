from django.test import SimpleTestCase
from django.urls import reverse, resolve
from .. import views


class TestUrls(SimpleTestCase):
    def test_index_url_resolves(self):
        url = reverse("home")
        self.assertEqual(resolve(url).func, views.index)

    def test_analytics_url_resolves(self):
        url = reverse("analytics")
        self.assertEqual(resolve(url).func, views.analytics)

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

    # def test_csv_export_url_resolves(self):
    #     url = reverse('export_csv')
    #     self.assertEqual(resolve(url).func, views.export_csv)

    def test_export_excel_url_resolves(self):
        url = reverse("export_excel")
        self.assertEqual(resolve(url).func, views.export_excel)

    def test_account_page_url_resolves(self):
        url = reverse("account")
        self.assertEqual(resolve(url).func, views.account)

    def test_note_main_url_resolves(self):
        url = reverse("notes")
        self.assertEqual(resolve(url).func, views.notes)

    def test_note_detail_url_resolves(self):
        url = reverse("note_detail", kwargs={"pk": 1})
        self.assertEqual(resolve(url).func, views.note_detail)

    def test_note_add_url_resolves(self):
        url = reverse("note_add")
        self.assertEqual(resolve(url).func, views.note_add)

    def test_note_edit_url_resolves(self):
        url = reverse("note_edit", kwargs={"pk": 1})
        self.assertEqual(resolve(url).func, views.note_edit)

    def test_note_delete_url_resolves(self):
        url = reverse("note_delete", kwargs={"pk": 1})
        self.assertEqual(resolve(url).func, views.note_delete)

    def test_note_personal_url_resolves(self):
        url = reverse("note_personal")
        self.assertEqual(resolve(url).func, views.note_personal)

    def test_note_tags_url_resolves(self):
        url = reverse("note_tags", kwargs={"slug": "test"})
        self.assertEqual(resolve(url).func, views.note_tags)

    def test_note_authors_url_resolves(self):
        url = reverse("note_authors", kwargs={"pk": 1})
        self.assertEqual(resolve(url).func, views.note_authors)

    def test_autocomplete_locations_url_resolves(self):
        url = reverse("autocomplete_locations")
        self.assertEqual(resolve(url).func, views.autocomplete_locations)

    def test_autocomplete_patient_id_url_resolves(self):
        url = reverse("autocomplete_patients")
        self.assertEqual(resolve(url).func, views.autocomplete_patient_id)

    def test_autocomplete_tags_url_resolves(self):
        url = reverse("autocomplete_tags")
        self.assertEqual(resolve(url).func, views.autocomplete_tags)

    def test_note_search_url_resolves(self):
        url = reverse("note_search")
        self.assertEqual(resolve(url).func, views.note_search)

    def test_barcode_url_resolves(self):
        url = reverse("barcode")
        self.assertEqual(resolve(url).func, views.barcode)

    def test_barcode_samples_used_url_resolves(self):
        url = reverse("barcode_samples_used")
        self.assertEqual(resolve(url).func, views.barcode_samples_used)

    def test_data_export_url_resolves(self):
        url = reverse("data_export")
        self.assertEqual(resolve(url).func, views.data_export)
