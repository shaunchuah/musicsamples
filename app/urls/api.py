from django.urls import include, path
from rest_framework import routers

from ..views import MultipleSampleViewSet, SampleIsUsedViewSet, SampleLocationViewSet

router = routers.DefaultRouter()

# Django Rest Framework API endpoints
router.register(r"sample_location", SampleLocationViewSet, "sample_location")
router.register(r"samples_used", SampleIsUsedViewSet, "samples_used")
router.register(r"multiple_samples", MultipleSampleViewSet, "multiple_samples")

urlpatterns = [
    path("api/", include(router.urls)),
]
