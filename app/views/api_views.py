from django.contrib.auth import authenticate
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from app.models import Sample
from app.pagination import SamplePageNumberPagination
from app.serializers import SampleV2Serializer, SampleV3Serializer


@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):
    email = request.data.get("email")
    password = request.data.get("password")

    user = authenticate(email=email, password=password)

    if user is not None:
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "status": "success",
                "user": {
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "is_staff": user.is_staff,
                    "is_superuser": user.is_superuser,
                    "groups": [group.name for group in user.groups.all()],
                },
                "token": str(refresh.access_token),
                "refresh": str(refresh),
                "expires_at": str(refresh.access_token.get("exp")),
            }
        )
    else:
        return Response({"status": "error", "message": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


class SampleV2ViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows samples to be viewed and edited
    Lookup field set to the barcode ID instead of the default Django
    autoincrementing id system
    """

    queryset = Sample.objects.filter(is_used=False).order_by("-sample_datetime")
    serializer_class = SampleV2Serializer
    lookup_field = "sample_id"
    filterset_fields = ["sample_type"]

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user.email,
            last_modified_by=self.request.user.email,
        )

    def perform_update(self, serializer):
        serializer.save(
            last_modified_by=self.request.user.email,
        )


class SampleV3ViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only API for the v3 frontend that exposes key sample details.
    """

    queryset = Sample.objects.order_by("-sample_datetime")
    serializer_class = SampleV3Serializer
    lookup_field = "sample_id"
    filterset_fields = [
        "study_name",
        "sample_type",
        "is_used",
    ]
    pagination_class = SamplePageNumberPagination
