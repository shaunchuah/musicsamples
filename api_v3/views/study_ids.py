# api_v3/views/study_ids.py
# Hosts the v3 study ID API endpoints used by the Next.js frontend.
# Exists to provide list/search/delete access for study identifiers without relying on template views.

from django.db.models import Count, Q
from drf_spectacular.utils import extend_schema
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api_v3.serializers import (
    StudyIdentifierFileSummaryV3Serializer,
    StudyIdentifierSampleSummaryV3Serializer,
    StudyIdentifierV3Serializer,
)
from app.models import DataStore, Sample, StudyIdentifier
from app.pagination import StudyIdPageNumberPagination


@extend_schema(tags=["v3"])
class StudyIdentifierV3ViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """
    API for the v3 frontend that exposes study identifier details.
    """

    queryset = StudyIdentifier.objects.order_by("name")
    serializer_class = StudyIdentifierV3Serializer
    permission_classes = [IsAuthenticated]
    filter_backends = [OrderingFilter]
    ordering_fields = [
        "name",
        "study_name",
        "study_group",
        "age",
        "sex",
        "study_center",
        "id",
    ]
    ordering = ["name"]
    pagination_class = StudyIdPageNumberPagination

    def get_queryset(self):
        return (
            StudyIdentifier.objects.annotate(
                sample_count=Count("samples", distinct=True),
                file_count=Count("files", distinct=True),
            )
            .order_by("name")
            .all()
        )

    def destroy(self, request, *args, **kwargs):
        user = getattr(request, "user", None)
        if not (getattr(user, "is_staff", False) or getattr(user, "is_superuser", False)):
            return Response({"detail": "Only staff can delete study IDs."}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

    @extend_schema(tags=["v3"], description="Search study IDs by name or study name.")
    @action(detail=False, methods=["get"], url_path="search")
    def search(self, request):
        query_string = request.query_params.get("query", "").strip()
        queryset = self.get_queryset()

        if query_string:
            queryset = queryset.filter(Q(name__icontains=query_string) | Q(study_name__icontains=query_string))

        queryset = self.filter_queryset(queryset)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(tags=["v3"], description="List samples linked to a study ID.")
    @action(detail=True, methods=["get"], url_path="samples")
    def samples(self, request, pk=None):
        study_id = self.get_object()
        queryset = Sample.objects.filter(study_id=study_id).order_by("sample_id")
        serializer = StudyIdentifierSampleSummaryV3Serializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(tags=["v3"], description="List files linked to a study ID.")
    @action(detail=True, methods=["get"], url_path="files")
    def files(self, request, pk=None):
        study_id = self.get_object()
        queryset = DataStore.objects.filter(study_id=study_id).order_by("formatted_file_name")
        serializer = StudyIdentifierFileSummaryV3Serializer(queryset, many=True)
        return Response(serializer.data)
