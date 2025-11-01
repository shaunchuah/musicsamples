from django.contrib.auth import authenticate
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from app.filters import SampleV3Filter
from app.models import Sample
from app.pagination import SamplePageNumberPagination
from app.serializers import SampleV3DetailSerializer, SampleV3Serializer
from core.clinical import get_samples_with_clinical_data


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


class SampleV3ViewSet(viewsets.ModelViewSet):
    """
    API for the v3 frontend that exposes key sample details.
    """

    # The ModelViewSet is read/write, so we must stamp audit metadata on mutations
    queryset = Sample.objects.order_by("-sample_datetime")
    serializer_class = SampleV3Serializer
    lookup_field = "sample_id"
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = SampleV3Filter
    ordering_fields = [
        "sample_datetime",
        "sample_id",
        "study_name",
        "sample_location",
        "sample_sublocation",
        "sample_type",
        "study_id__name",
        "id",
    ]
    ordering = ["-sample_datetime"]
    pagination_class = SamplePageNumberPagination

    def get_queryset(self):
        base_queryset = Sample.objects.select_related("study_id").order_by("-sample_datetime")
        action = getattr(self, "action", None)

        if action == "list":
            request = getattr(self, "request", None)
            include_used = False
            has_is_used_filter = False
            if request:
                include_used = request.query_params.get("include_used") == "true"
                has_is_used_filter = "is_used" in request.query_params
            if not include_used and not has_is_used_filter:
                base_queryset = base_queryset.filter(is_used=False)

        return get_samples_with_clinical_data(base_queryset)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return SampleV3DetailSerializer
        return super().get_serializer_class()

    def _current_user_identifier(self) -> str:
        """
        Returns the best available identifier for the authenticated user.
        """
        user = getattr(self.request, "user", None)
        if not user:
            return ""
        email = getattr(user, "email", "")
        if email:
            return email
        if hasattr(user, "get_username"):
            username = user.get_username()
            if username:
                return username
        return str(user)

    def perform_create(self, serializer):
        # Ensure both audit fields are populated during record creation
        user_identifier = self._current_user_identifier()
        serializer.save(created_by=user_identifier, last_modified_by=user_identifier)

    def perform_update(self, serializer):
        # Maintain audit trail by updating the modifier on each change
        serializer.save(last_modified_by=self._current_user_identifier())
