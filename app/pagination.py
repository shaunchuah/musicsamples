# app/pagination.py
# Defines DRF pagination classes tailored for sample endpoints consumed by the Next.js frontend.
# Ensures API responses stay capped at an agreed page size so the frontend can page predictably.

from django.conf import settings
from rest_framework.pagination import PageNumberPagination


class SamplePageNumberPagination(PageNumberPagination):
    """
    Page-number pagination limited to the configured sample page size.
    """

    page_size = getattr(settings, "SAMPLE_PAGINATION_SIZE", 50)
    page_size_query_param = "page_size"
    max_page_size = page_size
