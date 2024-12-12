from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Max, OuterRef, Subquery
from django.shortcuts import get_object_or_404, render
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAdminUser
from rest_framework.renderers import BrowsableAPIRenderer, JSONRenderer
from rest_framework.response import Response

from datasets.models import Dataset, DatasetAccessHistory, DatasetAnalytics, DataSourceStatusCheck
from datasets.permissions import CustomDjangoModelPermission
from datasets.serializers import DatasetAnalyticsSerializer, DatasetSerializer, DataSourceStatusCheckSerializer
from datasets.utils import export_json_field

User = get_user_model()


class DatasetCreateUpdateView(CreateAPIView):
    """
    View for creating or updating Dataset instances.
    This view creates a new Dataset instance or updates an existing one depending on
    whether a Dataset with the given 'name' already exists.
    """

    queryset = Dataset.objects.all()
    serializer_class = DatasetSerializer
    permission_classes = [IsAdminUser]
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]

    def create(self, request, *args, **kwargs):
        try:
            Dataset.objects.get(name=request.data["name"])
            return self.update(request, *args, **kwargs)
        except Dataset.DoesNotExist:
            return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = Dataset.objects.get(name=request.data["name"])
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)


class DatasetAnalyticsCreateUpdateView(CreateAPIView):
    """
    View for creating or updating DatasetAnalytics instances.
    This view creates a new DatasetAnalytics instance or updates an existing one depending on
    whether a DatasetAnalytics with the given 'name' already exists.
    """

    queryset = DatasetAnalytics.objects.all()
    serializer_class = DatasetAnalyticsSerializer
    permission_classes = [IsAdminUser]
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]

    def create(self, request, *args, **kwargs):
        try:
            DatasetAnalytics.objects.get(name=request.data["name"])
            return self.update(request, *args, **kwargs)
        except DatasetAnalytics.DoesNotExist:
            return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = DatasetAnalytics.objects.get(name=request.data["name"])
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)


class DataSourceStatusCheckView(CreateAPIView):
    """
    DataSourceStatusCheckView is a view that handles the creation of DataSourceStatusCheck objects.
    Permissions:
        Only users with admin privileges can access this view.
    """

    queryset = DataSourceStatusCheck.objects.all()
    serializer_class = DataSourceStatusCheckSerializer
    permission_classes = [IsAdminUser]
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]


@login_required
@permission_required("datasets.view_dataset", raise_exception=True)
def list_datasets(request):
    datasets = Dataset.objects.all().prefetch_related("datasetaccesshistory_set")
    site_url = settings.SITE_URL

    # Data Source Status Checks
    data_source_status_checks = DataSourceStatusCheck.objects.all()
    latest_status_checks = (
        data_source_status_checks.values("data_source").annotate(latest_checked_at=Max("checked_at")).order_by()
    )
    latest_status_checks = DataSourceStatusCheck.objects.filter(
        checked_at__in=[item["latest_checked_at"] for item in latest_status_checks]
    )

    # Select the 30 most recent checks for each unique data_source
    latest_checks = DataSourceStatusCheck.objects.filter(data_source=OuterRef("data_source")).order_by("-checked_at")
    last_30_checks = latest_checks[:30]
    graph_data = DataSourceStatusCheck.objects.filter(id__in=Subquery(last_30_checks.values("id")))

    # User Access List
    user_access_list = User.objects.filter(groups__name="datasets").order_by("first_name")

    return render(
        request,
        "datasets/datasets_list.html",
        {
            "datasets": datasets,
            "data_source_status_checks": latest_status_checks,
            "site_url": site_url,
            "graph_data": graph_data,
            "user_access_list": user_access_list,
        },
    )


@login_required
@permission_required("datasets.view_dataset", raise_exception=True)
def dataset_export_csv(request, dataset_name):
    dataset = get_object_or_404(Dataset, name=dataset_name)
    DatasetAccessHistory.objects.create(dataset=dataset, user=request.user, access_type="CSV")
    return export_json_field(dataset.name, dataset.json)


class RetrieveDatasetAPIView(RetrieveAPIView):
    lookup_field = "name"
    queryset = Dataset.objects.all()
    permission_classes = [CustomDjangoModelPermission]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        DatasetAccessHistory.objects.create(dataset=instance, user=request.user, access_type="JSON")
        return Response(instance.json)


@login_required
@permission_required("datasets.view_dataset", raise_exception=True)
def dataset_access_history(request, dataset_name):
    dataset = Dataset.objects.get(name=dataset_name)
    dataset_access_history = DatasetAccessHistory.objects.filter(dataset=dataset).order_by("-accessed")
    return render(
        request,
        "datasets/dataset_access_history.html",
        {"dataset_access_history": dataset_access_history, "dataset": dataset},
    )
