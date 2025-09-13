from django.urls import include, path
from rest_framework import routers
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from .. import views
from ..views import SampleV2ViewSet

router_v2 = routers.DefaultRouter()
router_v2.register(r"samples", SampleV2ViewSet, "samples")

urlpatterns = [
    # Prototype API
    path("api/v2/auth/login/", views.login_view, name="login"),
    path("api/v2/auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/v2/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("api/v2/", include(router_v2.urls)),
]
