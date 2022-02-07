from django.test import Client, TestCase
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed

from authentication.factories import UserFactory


class TestTemplates(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client = Client()
        self.client.force_login(self.user, backend=None)
        self.anonymous_client = Client()

    def test_index_page(self):
        url = reverse("home")
        response = self.client.get(url)
        assertTemplateUsed(response, "index.html")

    def test_account_page(self):
        path = reverse("account")
        response = self.client.get(path)
        assertTemplateUsed(response, "account.html")

    def test_used_samples_page(self):
        path = reverse("used_samples")
        response = self.client.get(path)
        assertTemplateUsed(response, "samples/used_samples.html")

    def test_barcode_main_page(self):
        path = reverse("barcode")
        response = self.client.get(path)
        assertTemplateUsed(response, "barcode.html")

    def test_barcode_samples_used_page(self):
        path = reverse("barcode_samples_used")
        response = self.client.get(path)
        assertTemplateUsed(response, "barcode-markused.html")

    def test_barcode_add_multiple_view(self):
        path = reverse("barcode_add_multiple")
        response = self.client.get(path)
        assertTemplateUsed(response, "barcode-addmultiple.html")

    def test_archive_page(self):
        path = reverse("sample_archive")
        response = self.client.get(path)
        assertTemplateUsed(response, "samples/sample-archive.html")

    def test_reference_page(self):
        path = reverse("reference")
        response = self.client.get(path)
        assertTemplateUsed(response, "reference.html")

    def test_analytics_authorized(self):
        path = reverse("analytics")
        response = self.client.get(path)
        assertTemplateUsed(response, "analytics.html")

    def test_gid_overview_page(self):
        path = reverse("gid_overview")
        response = self.client.get(path)
        assertTemplateUsed(response, "gid_overview.html")
