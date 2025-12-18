from drf_spectacular.utils import extend_schema
from rest_framework_simplejwt.views import TokenBlacklistView, TokenObtainPairView, TokenRefreshView


@extend_schema(tags=["v3"])
class V3TokenObtainPairView(TokenObtainPairView):
    pass


@extend_schema(tags=["v3"])
class V3TokenRefreshView(TokenRefreshView):
    pass


@extend_schema(tags=["v3"])
class V3TokenBlacklistView(TokenBlacklistView):
    pass
