# api_v3/views/experiments.py
# Hosts the v3 experiment API endpoints used by the Next.js frontend.
# Exists to provide read-only, filterable access to experiments without relying on Django templates.

from django.db.models import Q
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api_v3.serializers import ExperimentV3Serializer
from app.models import Experiment
from app.pagination import SamplePageNumberPagination
from core.utils.export import export_csv


@extend_schema(tags=["v3"])
class ExperimentV3ViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API for the v3 frontend that exposes key experiment details.
    """

    queryset = Experiment.objects.order_by("-created")
    serializer_class = ExperimentV3Serializer
    permission_classes = [IsAuthenticated]
    filter_backends = [OrderingFilter]
    ordering_fields = ["created", "date", "name", "basic_science_group", "id"]
    ordering = ["-created"]
    pagination_class = SamplePageNumberPagination

    def get_queryset(self):
        base_queryset = (
            Experiment.objects.prefetch_related("sample_types", "tissue_types", "boxes")
            .select_related("created_by", "last_modified_by")
            .order_by("-created")
        )
        action = getattr(self, "action", None)

        if action in ("list", "search"):
            request = getattr(self, "request", None)
            include_deleted = False
            has_deleted_filter = False
            if request:
                include_deleted = request.query_params.get("include_deleted") == "true"
                has_deleted_filter = "is_deleted" in request.query_params
            if not include_deleted and not has_deleted_filter:
                base_queryset = base_queryset.filter(is_deleted=False)

        return base_queryset

    @extend_schema(tags=["v3"], description="Search experiments by name or description.")
    @action(detail=False, methods=["get"], url_path="search")
    def search(self, request):
        query_string = request.query_params.get("query", "").strip()
        queryset = self.get_queryset()

        if query_string:
            queryset = queryset.filter(
                Q(name__icontains=query_string) | Q(description__icontains=query_string)
            ).distinct()

        queryset = self.filter_queryset(queryset)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


@extend_schema(tags=["v3"])
class ExperimentExportView(APIView):
    """
    Export filtered experiments as CSV to avoid paginated client aggregation.
    """

    permission_classes = [IsAuthenticated]
    ordering_fields = ["created", "date", "name", "basic_science_group", "id"]
    ordering = ["-created"]

    def get(self, request):
        base_queryset = (
            Experiment.objects.prefetch_related("sample_types", "tissue_types", "boxes")
            .select_related("created_by", "last_modified_by")
            .order_by("-created")
        )
        include_deleted = request.query_params.get("include_deleted") == "true"
        has_deleted_filter = "is_deleted" in request.query_params
        if not include_deleted and not has_deleted_filter:
            base_queryset = base_queryset.filter(is_deleted=False)

        query_string = request.query_params.get("query", "").strip()
        if query_string:
            base_queryset = base_queryset.filter(
                Q(name__icontains=query_string) | Q(description__icontains=query_string)
            ).distinct()

        queryset = OrderingFilter().filter_queryset(request, base_queryset, self)

        return export_csv(queryset, file_prefix="gtrac", file_name="experiments")
