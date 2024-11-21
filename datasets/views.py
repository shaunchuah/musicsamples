from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404, render
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAdminUser
from rest_framework.renderers import BrowsableAPIRenderer, JSONRenderer
from rest_framework.response import Response

from datasets.models import Dataset
from datasets.permissions import CustomDjangoModelPermission
from datasets.serializers import DatasetSerializer
from datasets.utils import export_json_field


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


@login_required
@permission_required("datasets.view_dataset", raise_exception=True)
def list_datasets(request):
    datasets = Dataset.objects.all()
    site_url = settings.SITE_URL
    return render(request, "datasets/datasets_list.html", {"datasets": datasets, "site_url": site_url})


@login_required
@permission_required("datasets.view_dataset", raise_exception=True)
def dataset_export_csv(request, dataset_name):
    dataset = get_object_or_404(Dataset, name=dataset_name)
    return export_json_field(dataset.name, dataset.json)


class RetrieveDatasetAPIView(RetrieveAPIView):
    lookup_field = "name"
    queryset = Dataset.objects.all()
    permission_classes = [CustomDjangoModelPermission]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        return Response(instance.json)
