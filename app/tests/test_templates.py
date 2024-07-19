from django.test import Client, TestCase
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed

from app.factories import SampleFactory
from authentication.factories import UserFactory


class TestTemplates(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client = Client()
        self.client.force_login(self.user, backend=None)
        self.anonymous_client = Client()

    @classmethod
    def setUpTestData(self):
        SampleFactory()

    def test_index_page(self):
        url = reverse("home")
        response = self.client.get(url)
        assertTemplateUsed(response, "index.html")

    def test_sample_search(self):
        path = reverse("sample_search")
        response = self.client.get(path)
        assertTemplateUsed(response, "index.html")

    def test_account_page(self):
        path = reverse("account")
        response = self.client.get(path)
        assertTemplateUsed(response, "account.html")

    def test_used_samples(self):
        path = reverse("used_samples")
        response = self.client.get(path)
        assertTemplateUsed(response, "samples/used_samples.html")

    def test_barcode_main(self):
        path = reverse("barcode")
        response = self.client.get(path)
        assertTemplateUsed(response, "barcode.html")

    def test_barcode_samples_used(self):
        path = reverse("barcode_samples_used")
        response = self.client.get(path)
        assertTemplateUsed(response, "barcode-markused.html")

    def test_barcode_add_multiple(self):
        path = reverse("barcode_add_multiple")
        response = self.client.get(path)
        assertTemplateUsed(response, "barcode-addmultiple.html")

    def test_archive(self):
        path = reverse("sample_archive")
        response = self.client.get(path)
        assertTemplateUsed(response, "samples/sample-archive.html")

    def test_reference(self):
        path = reverse("reference")
        response = self.client.get(path)
        assertTemplateUsed(response, "reference.html")

    def test_analytics(self):
        path = reverse("analytics")
        response = self.client.get(path)
        assertTemplateUsed(response, "analytics.html")

    def test_sample_delete(self):
        path = reverse("sample_delete", kwargs={"pk": 1})
        response = self.client.get(path)
        assertTemplateUsed(response, "samples/sample-delete.html")

    def test_sample_checkout(self):
        path = reverse("sample_checkout", kwargs={"pk": 1})
        response = self.client.get(path)
        assertTemplateUsed(response, "samples/sample-checkout.html")

    def test_error_404_template(self):
        path = "/doesnotexist.html"
        response = self.client.get(path)
        assert response.status_code == 404, "Check 404 is working."
