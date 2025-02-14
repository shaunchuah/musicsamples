from django.conf import settings
from django.test import Client, TestCase
from django.urls import reverse

from app.factories import SampleFactory
from users.factories import UserFactory

SAMPLE_PAGINATION_SIZE = settings.SAMPLE_PAGINATION_SIZE


class TestPagination(TestCase):
    """
    Tests Pagination for index, filter and used_samples

    Paginator reference
    https://simpleisbetterthancomplex.com/tutorial/2016/08/03/how-to-paginate-with-django.html
    """

    def setUp(self):
        self.user = UserFactory()
        self.client = Client()
        self.client.force_login(self.user, backend=None)
        self.anonymous_client = Client()

    @classmethod
    def setUpTestData(cls):
        # Set up a bank of samples and used samples
        # 2 pages of active samples and 3 pages of used samples
        # 5 total pages
        for i in range(0, SAMPLE_PAGINATION_SIZE + 10):
            SampleFactory()
        for i in range(0, (SAMPLE_PAGINATION_SIZE * 3)):
            SampleFactory(is_used=True)

    def test_index_page_and_pagination(self):
        url = reverse("home")
        response = self.client.get(url)
        assert response.context["page_obj"].paginator.num_pages == 2

    def test_index_page_not_an_integer(self):
        url = reverse("home") + "?page=notaninteger"
        response = self.client.get(url)
        assert response.context["page_obj"].next_page_number() == 2

    def test_index_page_empty_page(self):
        url = reverse("home") + "?page=10"
        response = self.client.get(url)
        assert response.context["page_obj"].has_next() is False

    def test_used_samples_total_page_count(self):
        url = reverse("used_samples")
        response = self.client.get(url)
        assert response.context["page_obj"].paginator.num_pages == 3

    def test_used_samples_page_not_an_integer(self):
        url = reverse("used_samples") + "?page=notaninteger"
        response = self.client.get(url)
        assert response.context["page_obj"].next_page_number() == 2

    def test_used_samples_page_empty_page(self):
        url = reverse("used_samples") + "?page=10"
        response = self.client.get(url)
        assert response.context["page_obj"].has_next() is False

    def test_filter_page_total_page_count(self):
        url = reverse("filter") + "?page=notaninteger"
        response = self.client.get(url)
        assert response.context["sample_list"].paginator.num_pages == 5

    def test_filter_page_not_an_integer(self):
        url = reverse("filter") + "?page=notaninteger"
        response = self.client.get(url)
        assert response.context["sample_list"].next_page_number() == 2

    def test_filter_page_empty_page(self):
        url = reverse("filter") + "?page=10"
        response = self.client.get(url)
        assert response.context["sample_list"].has_next() is False
