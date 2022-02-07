from django.test import Client, TestCase
from django.urls import reverse


class TestUnauthorized(TestCase):
    def setUp(self):
        self.client = Client()

    def test_home_page_unauthorized(self):
        path = reverse("home")
        response = self.client.get(path)
        assert response.status_code == 302
        assert "login" in response.url

    def test_analytics_unauthorized(self):
        path = reverse("analytics")
        response = self.client.get(path)
        assert response.status_code == 302
        assert "login" in response.url

    def test_reference_unauthorized(self):
        path = reverse("reference")
        response = self.client.get(path)
        assert response.status_code == 302
        assert "login" in response.url

    def test_archive_url_unauthorized(self):
        path = reverse("sample_archive")
        response = self.client.get(path)
        assert response.status_code == 302
        assert "login" in response.url

    def test_sample_add_unauthorized(self):
        path = reverse("sample_add")
        response = self.client.get(path)
        assert response.status_code == 302
        assert "login" in response.url

    def test_sample_detail_unauthorized(self):
        path = reverse("sample_detail", kwargs={"pk": 1})
        response = self.client.get(path)
        assert response.status_code == 302
        assert "login" in response.url

    def test_sample_edit_unauthorized(self):
        path = reverse("sample_edit", kwargs={"pk": 1})
        response = self.client.get(path)
        assert response.status_code == 302
        assert "login" in response.url

    def test_sample_delete_unauthorized(self):
        path = reverse("sample_delete", kwargs={"pk": 1})
        response = self.client.get(path)
        assert response.status_code == 302
        assert "login" in response.url

    def test_sample_restore_unauthorized(self):
        path = reverse("sample_restore", kwargs={"pk": 1})
        response = self.client.get(path)
        assert response.status_code == 302
        assert "login" in response.url

    def test_sample_checkout_unauthorized(self):
        path = reverse("sample_checkout", kwargs={"pk": 1})
        response = self.client.get(path)
        assert response.status_code == 302
        assert "login" in response.url

    def test_account_page_unauthorized(self):
        path = reverse("account")
        response = self.client.get(path)
        assert response.status_code == 302
        assert "login" in response.url
