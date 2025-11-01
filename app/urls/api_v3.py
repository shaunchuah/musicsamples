# app/urls/api_v3.py
# Defines the v3 API routes for sample data consumed by the new frontend.
# This file exists to provide a dedicated namespace for /api/v3/ endpoints.

from django.urls import include, path
from rest_framework import routers

from ..views import SampleV3ViewSet

router_v3 = routers.DefaultRouter()
router_v3.register(r"samples", SampleV3ViewSet, "v3-samples")

urlpatterns = [
    path("api/v3/", include(router_v3.urls)),
]
