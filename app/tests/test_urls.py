from django.test import TestCase, SimpleTestCase, Client
from ..models import Sample
from django.urls import reverse, resolve
from ..views import *

class TestUrls(SimpleTestCase):
    def test_index_url_resolves(self):
        url = reverse('home')
        self.assertEqual(resolve(url).func, index)

    def test_analytics_url_resolves(self):
        url = reverse('analytics')
        self.assertEqual(resolve(url).func, analytics)

    def test_reference_url_resolves(self):
        url = reverse('reference')
        self.assertEqual(resolve(url).func, reference)

    def test_archive_url_resolves(self):
        url = reverse('archive')
        self.assertEqual(resolve(url).func, archive)

    def test_add_sample_url_resolves(self):
        url = reverse('new_sample')
        self.assertEqual(resolve(url).func, add)

    def test_view_single_sample_url_resolves(self):
        url = reverse('sample_detail', kwargs={'pk':1})
        self.assertEqual(resolve(url).func, sample_detail)

    def test_edit_sample_url_resolves(self):
        url = reverse('sample_edit', kwargs={'pk':23})
        self.assertEqual(resolve(url).func, sample_edit)

    def test_delete_sample_url_resolves(self):
        url = reverse('delete', kwargs={'pk':3})
        self.assertEqual(resolve(url).func, delete)

    def test_restore_sample_url_resolves(self):
        url = reverse('restore', kwargs={'pk':3})
        self.assertEqual(resolve(url).func, restore)

    def test_checkout_sample_url_resolves(self):
        url = reverse('checkout', kwargs={'pk':3})
        self.assertEqual(resolve(url).func, checkout)

    def test_search_url_resolves(self):
        url = reverse('search')
        self.assertEqual(resolve(url).func, search)

    def test_csv_export_url_resolves(self):
        url = reverse('export_csv')
        self.assertEqual(resolve(url).func, export_csv)

    def test_export_excel_url_resolves(self):
        url = reverse('export_excel')
        self.assertEqual(resolve(url).func, export_excel)

    def test_account_page_url_resolves(self):
        url = reverse('account')
        self.assertEqual(resolve(url).func, account)
