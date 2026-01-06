# api_v3/views/boxes.py
# Hosts the v3 box API endpoints used by the Next.js frontend.
# Exists to provide read-only, filterable access to boxes without relying on Django templates.

from django.db.models import Prefetch, Q
from drf_spectacular.utils import extend_schema
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api_v3.serializers import (
    BasicScienceBoxCreateV3Serializer,
    BasicScienceBoxDetailV3Serializer,
    BasicScienceBoxV3Serializer,
)
from app.choices import (
    BasicScienceBoxTypeChoices,
    ColumnChoices,
    DepthChoices,
    FreezerLocationChoices,
    RowChoices,
)
from app.models import BasicScienceBox, Experiment
from app.pagination import SamplePageNumberPagination
from core.utils.export import export_csv

EXPERIMENT_PREFETCH = Prefetch(
    "experiments",
    queryset=Experiment.objects.prefetch_related("sample_types", "tissue_types"),
)


@extend_schema(tags=["v3"])
class BasicScienceBoxV3ViewSet(mixins.CreateModelMixin, viewsets.ReadOnlyModelViewSet):
    """
    API for the v3 frontend that exposes key box details and creation.
    """

    queryset = BasicScienceBox.objects.order_by("-created")
    serializer_class = BasicScienceBoxV3Serializer
    permission_classes = [IsAuthenticated]
    filter_backends = [OrderingFilter]
    ordering_fields = ["created", "box_id", "location", "box_type", "id"]
    ordering = ["-created"]
    pagination_class = SamplePageNumberPagination

    def get_queryset(self):
        base_queryset = (
            BasicScienceBox.objects.prefetch_related(EXPERIMENT_PREFETCH)
            .select_related("created_by", "last_modified_by")
            .order_by("-created")
        )
        action = getattr(self, "action", None)

        if action in ("list", "search"):
            request = getattr(self, "request", None)
            include_used = False
            has_is_used_filter = False
            if request:
                include_used = request.query_params.get("include_used") == "true"
                has_is_used_filter = "is_used" in request.query_params
            if not include_used and not has_is_used_filter:
                base_queryset = base_queryset.filter(is_used=False)

        return base_queryset

    def get_serializer_class(self):
        if self.action == "create":
            return BasicScienceBoxCreateV3Serializer
        if self.action == "retrieve":
            return BasicScienceBoxDetailV3Serializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, last_modified_by=self.request.user)

    @extend_schema(tags=["v3"], description="Search boxes by common identifiers and text fields.")
    @action(detail=False, methods=["get"], url_path="search")
    def search(self, request):
        query_string = request.query_params.get("query", "").strip()
        queryset = self.get_queryset()

        if query_string:
            queryset = queryset.filter(
                Q(box_id__icontains=query_string)
                | Q(location__icontains=query_string)
                | Q(comments__icontains=query_string)
                | Q(experiments__basic_science_group__icontains=query_string)
                | Q(experiments__name__icontains=query_string)
                | Q(experiments__sample_types__name__icontains=query_string)
                | Q(experiments__tissue_types__name__icontains=query_string)
            ).distinct()

        queryset = self.filter_queryset(queryset)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


@extend_schema(tags=["v3"])
class BasicScienceBoxOptionsView(APIView):
    """
    Provides choice metadata required to populate the basic science box form.
    """

    permission_classes = [IsAuthenticated]

    @staticmethod
    def _format_choices(choices):
        return [{"value": value, "label": label} for value, label in choices]

    def get(self, request):
        experiments = Experiment.objects.filter(is_deleted=False).order_by("name")
        experiment_options = [
            {
                "id": experiment.id,
                "label": f"{experiment.name} ({experiment.get_basic_science_group_display()})",
            }
            for experiment in experiments
        ]
        payload = {
            "box_type_options": self._format_choices(BasicScienceBoxTypeChoices.choices),
            "location_options": self._format_choices(FreezerLocationChoices.choices),
            "row_options": self._format_choices(RowChoices.choices),
            "column_options": self._format_choices(ColumnChoices.choices),
            "depth_options": self._format_choices(DepthChoices.choices),
            "experiments": experiment_options,
        }
        return Response(payload)


@extend_schema(tags=["v3"])
class BasicScienceBoxExportView(APIView):
    """
    Export filtered boxes as CSV to avoid paginated client aggregation.
    """

    permission_classes = [IsAuthenticated]
    ordering_fields = ["created", "box_id", "location", "box_type", "id"]
    ordering = ["-created"]

    def get(self, request):
        base_queryset = (
            BasicScienceBox.objects.prefetch_related(EXPERIMENT_PREFETCH)
            .select_related("created_by", "last_modified_by")
            .order_by("-created")
        )
        include_used = request.query_params.get("include_used") == "true"
        has_is_used_filter = "is_used" in request.query_params
        if not include_used and not has_is_used_filter:
            base_queryset = base_queryset.filter(is_used=False)

        query_string = request.query_params.get("query", "").strip()
        if query_string:
            base_queryset = base_queryset.filter(
                Q(box_id__icontains=query_string)
                | Q(location__icontains=query_string)
                | Q(comments__icontains=query_string)
                | Q(experiments__basic_science_group__icontains=query_string)
                | Q(experiments__name__icontains=query_string)
                | Q(experiments__sample_types__name__icontains=query_string)
                | Q(experiments__tissue_types__name__icontains=query_string)
            ).distinct()

        queryset = OrderingFilter().filter_queryset(request, base_queryset, self)

        return export_csv(queryset, file_prefix="gtrac", file_name="basic_science_boxes")
