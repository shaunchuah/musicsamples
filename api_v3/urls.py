# api_v3/urls.py
# Defines the v3 API routes consumed by the Next.js frontend, including samples and auth/user helpers.
# Exists to provide a single namespace for frontend-facing endpoints while legacy Django template routes remain unchanged.

from django.urls import include, path
from rest_framework import routers

from api_v3.views import (
    CurrentUserView,
    SampleV3ViewSet,
    V3TokenBlacklistView,
    V3TokenObtainPairView,
    V3TokenRefreshView,
)

router = routers.DefaultRouter()
router.register(r"samples", SampleV3ViewSet, "v3-samples")

urlpatterns = [
    path("", include(router.urls)),
    path("users/me/", CurrentUserView.as_view(), name="v3-current-user"),
    path("auth/login/", V3TokenObtainPairView.as_view(), name="v3-token-obtain-pair"),
    path("auth/refresh/", V3TokenRefreshView.as_view(), name="v3-token-refresh"),
    path("auth/blacklist/", V3TokenBlacklistView.as_view(), name="v3-token-blacklist"),
]
