# api_v3/views/samples.py
# Hosts the v3 sample API endpoints used by the Next.js frontend, including list/detail and CRUD with audit stamping.
# Exists to decouple the API surface from legacy template views while keeping feature parity for samples.

from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import mixins, viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api_v3.serializers import (
    MultipleSampleV3Serializer,
    SampleIsUsedV3Serializer,
    SampleLocationV3Serializer,
    SampleV3DetailSerializer,
    SampleV3Serializer,
    SampleV3UpdateSerializer,
)
from app.filters import SampleV3Filter
from app.models import Sample, StudyIdentifier
from app.pagination import SamplePageNumberPagination
from core.clinical import get_samples_with_clinical_data


@extend_schema(tags=["v3"])
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
        if self.action in ("update", "partial_update"):
            return SampleV3UpdateSerializer
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


@extend_schema(tags=["v3"])
class SampleLocationV3ViewSet(mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """
    Update sample locations via QR scan workflows.
    """

    queryset = Sample.objects.all()
    serializer_class = SampleLocationV3Serializer
    lookup_field = "sample_id"
    permission_classes = [IsAuthenticated]

    def _current_user_identifier(self) -> str:
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

    def perform_update(self, serializer):
        serializer.save(last_modified_by=self._current_user_identifier())


@extend_schema(tags=["v3"])
class SampleIsUsedV3ViewSet(mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """
    Mark samples as used via QR scan workflows.
    """

    queryset = Sample.objects.all()
    serializer_class = SampleIsUsedV3Serializer
    lookup_field = "sample_id"
    permission_classes = [IsAuthenticated]

    def _current_user_identifier(self) -> str:
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

    def perform_update(self, serializer):
        serializer.save(last_modified_by=self._current_user_identifier())


@extend_schema(tags=["v3"])
class MultipleSampleV3ViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    Create samples via the bulk QR scan workflow.
    """

    queryset = Sample.objects.all()
    serializer_class = MultipleSampleV3Serializer
    permission_classes = [IsAuthenticated]

    def _current_user_identifier(self) -> str:
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
        user_identifier = self._current_user_identifier()
        serializer.save(created_by=user_identifier, last_modified_by=user_identifier)


@extend_schema(tags=["v3"])
class SampleLocationAutocompleteView(APIView):
    """
    Return location suggestions for sample forms.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        term = request.query_params.get("term")
        if term:
            queryset = (
                Sample.objects.filter(sample_location__icontains=term)
                .order_by()
                .values_list("sample_location", flat=True)
                .distinct()
            )
        else:
            queryset = Sample.objects.all().order_by().values_list("sample_location", flat=True).distinct()
        return Response([value for value in queryset if value])


@extend_schema(tags=["v3"])
class SampleSublocationAutocompleteView(APIView):
    """
    Return sublocation suggestions for sample forms.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        term = request.query_params.get("term")
        if term:
            queryset = (
                Sample.objects.filter(sample_sublocation__icontains=term)
                .order_by()
                .values_list("sample_sublocation", flat=True)
                .distinct()
            )
        else:
            queryset = Sample.objects.all().order_by().values_list("sample_sublocation", flat=True).distinct()
        return Response([value for value in queryset if value])


@extend_schema(tags=["v3"])
class StudyIdAutocompleteView(APIView):
    """
    Return study ID suggestions for sample forms.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        term = request.query_params.get("term")
        if term:
            queryset = StudyIdentifier.objects.filter(name__icontains=term).values_list("name", flat=True)
        else:
            queryset = StudyIdentifier.objects.all().values_list("name", flat=True)
        return Response([value for value in queryset if value])
