from django.test import SimpleTestCase
from django.urls import reverse, resolve
from .. import views


class TestUrls(SimpleTestCase):
    def test_index_url_resolves(self):
        url = reverse('home')
        self.assertEqual(resolve(url).func, views.index)

    def test_analytics_url_resolves(self):
        url = reverse('analytics')
        self.assertEqual(resolve(url).func, views.analytics)

    def test_reference_url_resolves(self):
        url = reverse('reference')
        self.assertEqual(resolve(url).func, views.reference)

    def test_archive_url_resolves(self):
        url = reverse('archive')
        self.assertEqual(resolve(url).func, views.archive)

    def test_add_sample_url_resolves(self):
        url = reverse('sample_add')
        self.assertEqual(resolve(url).func, views.sample_add)

    def test_view_single_sample_url_resolves(self):
        url = reverse('sample_detail', kwargs={'pk': 1})
        self.assertEqual(resolve(url).func, views.sample_detail)

    def test_edit_sample_url_resolves(self):
        url = reverse('sample_edit', kwargs={'pk': 23})
        self.assertEqual(resolve(url).func, views.sample_edit)

    def test_delete_sample_url_resolves(self):
        url = reverse('sample_delete', kwargs={'pk': 3})
        self.assertEqual(resolve(url).func, views.delete)

    def test_restore_sample_url_resolves(self):
        url = reverse('sample_restore', kwargs={'pk': 3})
        self.assertEqual(resolve(url).func, views.restore)

    def test_checkout_sample_url_resolves(self):
        url = reverse('checkout', kwargs={'pk': 3})
        self.assertEqual(resolve(url).func, views.checkout)

    def test_search_url_resolves(self):
        url = reverse('search')
        self.assertEqual(resolve(url).func, views.search)

    # def test_csv_export_url_resolves(self):
    #     url = reverse('export_csv')
    #     self.assertEqual(resolve(url).func, views.export_csv)

    def test_export_excel_url_resolves(self):
        url = reverse('export_excel')
        self.assertEqual(resolve(url).func, views.export_excel)

    def test_account_page_url_resolves(self):
        url = reverse('account')
        self.assertEqual(resolve(url).func, views.account)

    def test_notes_main_url_resolves(self):
        url = reverse('notes')
        self.assertEqual(resolve(url).func, views.notes)
