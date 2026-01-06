# api_v3/urls.py
# Defines the v3 API routes consumed by the Next.js frontend, including samples and auth/user helpers.
# Exists to provide a single namespace for frontend-facing endpoints while legacy Django template routes remain unchanged.

from django.urls import include, path
from rest_framework import routers

from api_v3.views import (
    BasicScienceBoxExportView,
    BasicScienceBoxFilterOptionsView,
    BasicScienceBoxOptionsView,
    BasicScienceBoxV3ViewSet,
    CurrentUserRecentSamplesView,
    CurrentUserTokenViewSet,
    CurrentUserView,
    ExperimentExportView,
    ExperimentFilterOptionsView,
    ExperimentOptionsView,
    ExperimentV3ViewSet,
    ManagementUserEmailsView,
    MultipleSampleV3ViewSet,
    PasswordChangeView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    SampleIsUsedV3ViewSet,
    SampleExportView,
    SampleLocationV3ViewSet,
    SampleLocationAutocompleteView,
    SampleSublocationAutocompleteView,
    SampleFilterOptionsView,
    SampleV3ViewSet,
    StaffUserViewSet,
    StudyIdAutocompleteView,
    V3TokenBlacklistView,
    V3TokenObtainPairView,
    V3TokenRefreshView,
)

router = routers.DefaultRouter()
router.register(r"boxes", BasicScienceBoxV3ViewSet, "v3-boxes")
router.register(r"experiments", ExperimentV3ViewSet, "v3-experiments")
router.register(r"samples", SampleV3ViewSet, "v3-samples")
router.register(r"multiple-samples", MultipleSampleV3ViewSet, "v3-multiple-samples")
router.register(r"samples-used", SampleIsUsedV3ViewSet, "v3-samples-used")
router.register(r"sample-location", SampleLocationV3ViewSet, "v3-sample-location")
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
    path(
        "samples/autocomplete/locations/",
        SampleLocationAutocompleteView.as_view(),
        name="v3-sample-location-autocomplete",
    ),
    path(
        "samples/autocomplete/sublocations/",
        SampleSublocationAutocompleteView.as_view(),
        name="v3-sample-sublocation-autocomplete",
    ),
    path(
        "samples/autocomplete/study-ids/",
        StudyIdAutocompleteView.as_view(),
        name="v3-study-id-autocomplete",
    ),
    path("boxes/export/", BasicScienceBoxExportView.as_view(), name="v3-boxes-export"),
    path("boxes/filters/", BasicScienceBoxFilterOptionsView.as_view(), name="v3-boxes-filter-options"),
    path("boxes/options/", BasicScienceBoxOptionsView.as_view(), name="v3-boxes-options"),
    path("experiments/export/", ExperimentExportView.as_view(), name="v3-experiments-export"),
    path("experiments/filters/", ExperimentFilterOptionsView.as_view(), name="v3-experiments-filter-options"),
    path("experiments/options/", ExperimentOptionsView.as_view(), name="v3-experiments-options"),
    path("samples/export/", SampleExportView.as_view(), name="v3-samples-export"),
    path("samples/filters/", SampleFilterOptionsView.as_view(), name="v3-sample-filter-options"),
    path("users/password-reset/", PasswordResetRequestView.as_view(), name="v3-password-reset"),
    path("users/password-reset/confirm/", PasswordResetConfirmView.as_view(), name="v3-password-reset-confirm"),
    path("management/user-emails/", ManagementUserEmailsView.as_view(), name="v3-management-user-emails"),
    path("auth/login/", V3TokenObtainPairView.as_view(), name="v3-token-obtain-pair"),
    path("auth/refresh/", V3TokenRefreshView.as_view(), name="v3-token-refresh"),
    path("auth/blacklist/", V3TokenBlacklistView.as_view(), name="v3-token-blacklist"),
    path("", include(router.urls)),
]
