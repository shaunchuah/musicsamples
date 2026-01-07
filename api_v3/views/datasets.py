# api_v3/views/datasets.py
# Provides v3 dataset endpoints for listings, exports, access history, and dashboard overview data.
# Exists to supply the Next.js datasets experience without modifying legacy Django template views.

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Count, Max
from rest_framework import viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from api_v3.serializers import DatasetAccessHistoryV3Serializer, DatasetListV3Serializer
from datasets.models import DataSourceStatusCheck, Dataset, DatasetAccessHistory, DatasetAccessTypeChoices
from datasets.permissions import CustomDjangoModelPermission
from datasets.utils import export_json_field

User = get_user_model()


class DatasetV3ViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for listing dataset metadata and returning dataset JSON payloads.
    """

    queryset = Dataset.objects.all().annotate(access_count=Count("datasetaccesshistory"))
    serializer_class = DatasetListV3Serializer
    permission_classes = [CustomDjangoModelPermission]
    lookup_field = "name"

    def retrieve(self, request, *args, **kwargs):
        dataset = self.get_object()
        DatasetAccessHistory.objects.create(
            dataset=dataset,
            user=request.user,
            access_type=DatasetAccessTypeChoices.JSON,
        )
        return Response(dataset.json)

    @action(detail=True, methods=["get"], url_path="export-csv")
    def export_csv(self, request, name=None):
        dataset = self.get_object()
        DatasetAccessHistory.objects.create(
            dataset=dataset,
            user=request.user,
            access_type=DatasetAccessTypeChoices.CSV,
        )
        return export_json_field(dataset.name, dataset.json)

    @action(detail=True, methods=["get"], url_path="access-history")
    def access_history(self, request, name=None):
        dataset = self.get_object()
        access_history = (
            DatasetAccessHistory.objects.filter(dataset=dataset).select_related("user").order_by("-accessed")
        )
        serializer = DatasetAccessHistoryV3Serializer(access_history, many=True)
        return Response(
            {
                "dataset": dataset.name,
                "access_count": access_history.count(),
                "results": serializer.data,
            }
        )


class DatasetOverviewView(GenericAPIView):
    """
    Combined overview endpoint returning datasets, status checks, access list, and API token.
    """

    queryset = Dataset.objects.all()
    permission_classes = [CustomDjangoModelPermission]

    def get(self, request):
        datasets = Dataset.objects.all().annotate(access_count=Count("datasetaccesshistory")).order_by("name")
        dataset_payload = DatasetListV3Serializer(datasets, many=True).data

        latest_checks = DataSourceStatusCheck.objects.values("data_source").annotate(
            latest_checked_at=Max("checked_at")
        )
        latest_checks = DataSourceStatusCheck.objects.filter(
            checked_at__in=[item["latest_checked_at"] for item in latest_checks]
        )

        status_payload = []
        for check in latest_checks.order_by("data_source"):
            recent_checks = list(
                DataSourceStatusCheck.objects.filter(data_source=check.data_source).order_by("-checked_at")[:30]
            )
            recent_statuses = [entry.response_status for entry in reversed(recent_checks)]
            status_payload.append(
                {
                    "data_source": check.data_source,
                    "response_status": check.response_status,
                    "error_message": check.error_message,
                    "checked_at": check.checked_at,
                    "recent_statuses": recent_statuses,
                }
            )

        user_access_list = User.objects.filter(groups__name="datasets").order_by("first_name", "last_name")
        user_payload = [
            {"first_name": user.first_name, "last_name": user.last_name, "email": user.email}
            for user in user_access_list
        ]

        token = Token.objects.filter(user=request.user).first()

        return Response(
            {
                "datasets": dataset_payload,
                "status_checks": status_payload,
                "user_access_list": user_payload,
                "site_url": settings.SITE_URL,
                "token": token.key if token else None,
            }
        )
