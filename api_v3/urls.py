# api_v3/urls.py
# Defines the v3 API routes consumed by the Next.js frontend, including samples and auth/user helpers.
# Exists to provide a single namespace for frontend-facing endpoints while legacy Django template routes remain unchanged.

from django.urls import include, path
from rest_framework import routers

from api_v3.views import (
    CurrentUserRecentSamplesView,
    CurrentUserTokenViewSet,
    CurrentUserView,
    ManagementUserEmailsView,
    PasswordChangeView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    SampleV3ViewSet,
    StaffUserViewSet,
    V3TokenBlacklistView,
    V3TokenObtainPairView,
    V3TokenRefreshView,
)

router = routers.DefaultRouter()
router.register(r"samples", SampleV3ViewSet, "v3-samples")
router.register(r"users", StaffUserViewSet, "v3-users")

urlpatterns = [
    path("users/me/", CurrentUserView.as_view(), name="v3-current-user"),
    path("users/me/password/", PasswordChangeView.as_view(), name="v3-password-change"),
    path(
        "users/me/token/",
        CurrentUserTokenViewSet.as_view({"post": "create", "delete": "destroy"}),
        name="v3-current-user-token",
    ),
    path(
        "users/me/token/refresh/",
        CurrentUserTokenViewSet.as_view({"post": "refresh"}),
        name="v3-current-user-token-refresh",
    ),
    path("users/me/recent-samples/", CurrentUserRecentSamplesView.as_view(), name="v3-current-user-recent-samples"),
    path("users/password-reset/", PasswordResetRequestView.as_view(), name="v3-password-reset"),
    path("users/password-reset/confirm/", PasswordResetConfirmView.as_view(), name="v3-password-reset-confirm"),
    path("management/user-emails/", ManagementUserEmailsView.as_view(), name="v3-management-user-emails"),
    path("auth/login/", V3TokenObtainPairView.as_view(), name="v3-token-obtain-pair"),
    path("auth/refresh/", V3TokenRefreshView.as_view(), name="v3-token-refresh"),
    path("auth/blacklist/", V3TokenBlacklistView.as_view(), name="v3-token-blacklist"),
    path("", include(router.urls)),
]
