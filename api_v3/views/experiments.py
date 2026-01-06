# api_v3/views/experiments.py
# Hosts the v3 experiment API endpoints used by the Next.js frontend.
# Exists to provide read-only, filterable access to experiments without relying on Django templates.

from django.db.models import Q
from drf_spectacular.utils import extend_schema
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api_v3.serializers import (
    ExperimentCreateV3Serializer,
    ExperimentDetailV3Serializer,
    ExperimentUpdateV3Serializer,
    ExperimentV3Serializer,
)
from app.choices import BasicScienceGroupChoices, SpeciesChoices
from app.filters import ExperimentFilter
from app.models import BasicScienceSampleType, Experiment, TissueType
from app.pagination import SamplePageNumberPagination
from core.utils.export import export_csv


@extend_schema(tags=["v3"])
class ExperimentV3ViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """
    API for the v3 frontend that exposes key experiment details.
    """

    queryset = Experiment.objects.order_by("-created")
    serializer_class = ExperimentV3Serializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = ExperimentFilter
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

    def get_serializer_class(self):
        if self.action == "create":
            return ExperimentCreateV3Serializer
        if self.action in ("update", "partial_update"):
            return ExperimentUpdateV3Serializer
        if self.action == "retrieve":
            return ExperimentDetailV3Serializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, last_modified_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(last_modified_by=self.request.user)

    def destroy(self, request, *args, **kwargs):
        experiment = self.get_object()
        experiment.is_deleted = True
        experiment.last_modified_by = request.user
        experiment.save(update_fields=["is_deleted", "last_modified_by", "last_modified"])
        serializer = self.get_serializer(experiment)
        return Response(serializer.data)

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

        queryset = ExperimentFilter(request.query_params, queryset=base_queryset).qs
        queryset = OrderingFilter().filter_queryset(request, queryset, self)

        return export_csv(queryset, file_prefix="gtrac", file_name="experiments")


@extend_schema(tags=["v3"])
class ExperimentOptionsView(APIView):
    """
    Provides choice metadata required to populate the experiment form.
    """

    permission_classes = [IsAuthenticated]

    @staticmethod
    def _format_choices(choices):
        return [{"value": value, "label": label} for value, label in choices]

    @staticmethod
    def _model_options(queryset, label_attr="name"):
        options = []
        for item in queryset:
            label = getattr(item, label_attr, None) or getattr(item, "name", None)
            options.append({"value": str(item.id), "label": label})
        return options

    def get(self, request):
        sample_types = BasicScienceSampleType.objects.order_by("name")
        tissue_types = TissueType.objects.order_by("name")
        payload = {
            "basic_science_group_options": self._format_choices(BasicScienceGroupChoices.choices),
            "species_options": self._format_choices(SpeciesChoices.choices),
            "sample_types": self._model_options(sample_types, label_attr="label"),
            "tissue_types": self._model_options(tissue_types, label_attr="label"),
        }
        return Response(payload)


@extend_schema(tags=["v3"])
class ExperimentFilterOptionsView(APIView):
    """
    Return dropdown-ready filter options for the experiments dashboard.
    """

    permission_classes = [IsAuthenticated]

    @staticmethod
    def _choice_options(choices):
        return [{"value": value, "label": label} for value, label in choices]

    @staticmethod
    def _model_options(queryset, label_attr="name"):
        options = []
        for item in queryset:
            label = getattr(item, label_attr, None) or getattr(item, "name", None)
            options.append({"value": str(item.id), "label": label})
        return options

    def get(self, request):
        boolean_options = [
            {"value": "true", "label": "Yes"},
            {"value": "false", "label": "No"},
        ]
        sample_types = BasicScienceSampleType.objects.order_by("name")
        tissue_types = TissueType.objects.order_by("name")
        return Response(
            {
                "basic_science_group": self._choice_options(BasicScienceGroupChoices.choices),
                "species": self._choice_options(SpeciesChoices.choices),
                "sample_types": self._model_options(sample_types, label_attr="label"),
                "tissue_types": self._model_options(tissue_types, label_attr="label"),
                "boolean": boolean_options,
            }
        )
