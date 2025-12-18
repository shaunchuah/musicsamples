from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenBlacklistView, TokenObtainPairView, TokenRefreshView

User = get_user_model()


class CurrentUserSerializer(serializers.ModelSerializer):
    groups = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "is_staff", "is_superuser", "groups")

    def get_groups(self, obj) -> list[str]:
        return list(obj.groups.values_list("name", flat=True))


@extend_schema(tags=["v3"])
class CurrentUserView(APIView):
    serializer_class = CurrentUserSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = CurrentUserSerializer(request.user)
        return Response(serializer.data)


@extend_schema(tags=["v3"])
class V3TokenObtainPairView(TokenObtainPairView):
    pass


@extend_schema(tags=["v3"])
class V3TokenRefreshView(TokenRefreshView):
    pass


@extend_schema(tags=["v3"])
class V3TokenBlacklistView(TokenBlacklistView):
    pass
