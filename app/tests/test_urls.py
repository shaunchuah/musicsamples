from django.test import TestCase, SimpleTestCase, Client
from ..models import Sample
from django.urls import reverse, resolve
from ..views import *

class TestUrls(SimpleTestCase):
    def test_index_url_resolves(self):
        url = reverse('home')
        self.assertEquals(resolve(url).func, index)

    def test_analytics_url_resolves(self):
        url = reverse('analytics')
        self.assertEquals(resolve(url).func, analytics)

    def test_reference_url_resolves(self):
        url = reverse('reference')
        self.assertEquals(resolve(url).func, reference)

    def test_archive_url_resolves(self):
        url = reverse('archive')
        self.assertEquals(resolve(url).func, archive)

    def test_add_sample_url_resolves(self):
        url = reverse('new_sample')
        self.assertEquals(resolve(url).func, add)

    def test_view_single_sample_url_resolves(self):
        url = reverse('sample_detail', kwargs={'pk':1})
        self.assertEquals(resolve(url).func, sample_detail)

    def test_edit_sample_url_resolves(self):
        url = reverse('sample_edit', kwargs={'pk':23})
        self.assertEquals(resolve(url).func, sample_edit)

    def test_delete_sample_url_resolves(self):
        url = reverse('delete', kwargs={'pk':3})
        self.assertEquals(resolve(url).func, delete)

    def test_restore_sample_url_resolves(self):
        url = reverse('restore', kwargs={'pk':3})
        self.assertEquals(resolve(url).func, restore)

    def test_checkout_sample_url_resolves(self):
        url = reverse('checkout', kwargs={'pk':3})
        self.assertEquals(resolve(url).func, checkout)

    def test_search_url_resolves(self):
        url = reverse('search')
        self.assertEquals(resolve(url).func, search)
    
    def test_bulkadd_url_resolves(self):
        url = reverse('bulkadd')
        self.assertEquals(resolve(url).func, bulkadd)

    def test_csv_export_url_resolves(self):
        url = reverse('export_csv')
        self.assertEquals(resolve(url).func, export_csv)

    def test_export_excel_add_url_resolves(self):
        url = reverse('export_excel_all')
        self.assertEquals(resolve(url).func, export_excel_all)

    def test_export_excel_url_resolves(self):
        url = reverse('export_excel')
        self.assertEquals(resolve(url).func, export_excel)
