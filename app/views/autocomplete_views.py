from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import viewsets

from app.models import Sample
from app.serializers import (
    MultipleSampleSerializer,
    SampleExportSerializer,
    SampleIsUsedSerializer,
    SampleSerializer,
)

#############################################################################
# AUTOCOMPLETE/AJAX SECTION #################################################
#############################################################################


@login_required(login_url="/login/")
def autocomplete_locations(request):
    # Helps speed up sample adding by autocompleting already existing locations
    if "term" in request.GET:
        qs = (
            Sample.objects.filter(sample_location__icontains=request.GET.get("term"))
            .order_by()
            .values("sample_location")
            .distinct()
        )
    else:
        qs = Sample.objects.all().order_by().values("sample_location").distinct()
    locations = []
    for sample in qs:
        locations.append(sample["sample_location"])
    return JsonResponse(locations, safe=False)


@login_required(login_url="/login/")
def autocomplete_sublocations(request):
    if "term" in request.GET:
        qs = (
            Sample.objects.filter(sample_sublocation__icontains=request.GET.get("term"))
            .order_by()
            .values("sample_sublocation")
            .distinct()
        )
    else:
        qs = Sample.objects.all().order_by().values("sample_sublocation").distinct()
    sublocations = []
    for sample in qs:
        sublocations.append(sample["sample_sublocation"])
    return JsonResponse(sublocations, safe=False)


@login_required(login_url="/login/")
def autocomplete_patient_id(request):
    # Helps speed up sample adding by locating existing patient IDs
    if "term" in request.GET:
        qs = (
            Sample.objects.filter(patient_id__icontains=request.GET.get("term"))
            .order_by()
            .values("patient_id")
            .distinct()
        )
    else:
        qs = Sample.objects.all().order_by().values("patient_id").distinct()
    patients = []
    for sample in qs:
        patients.append(sample["patient_id"])
    return JsonResponse(patients, safe=False)


##############################################################################
# REST FRAMEWORK/BARCODE APIS ################################################
##############################################################################
# The bulk QR scanning capability is dependent on using JavaScript - jQuery in
# this instance - in the frontend and Django Rest Framework in the backend.
#
# Barcode readers typically terminate the scan with either the 'enter' or
# 'tab' key.
#
# The barcode scanning page listens for both enter and tab keys
#
# When these keys are heard an ajax query is sent to the API /api/<Sample ID>/
# This attempts to match the scanned label against an existing sample and
# if so updates the sample's location.
# If it does not succeed it returns an error response - Object not found.
# A warning message is then displayed.
#
# This allows you to install physical hardpoints - eg arrival and departure
# from sites and if you scan every sample that goes through you can begin to
# track all their locations.


class SampleViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows samples to be viewed and edited
    Lookup field set to the barcode ID instead of the default Django
    autoincrementing id system
    """

    queryset = Sample.objects.all()
    serializer_class = SampleSerializer
    lookup_field = "sample_id"
    filterset_fields = ["sample_type"]

    def perform_update(self, serializer):
        serializer.save(
            last_modified_by=self.request.user.email,
        )


class SampleIsUsedViewSet(viewsets.ModelViewSet):
    queryset = Sample.objects.all()
    serializer_class = SampleIsUsedSerializer
    lookup_field = "sample_id"

    def perform_update(self, serializer):
        serializer.save(
            last_modified_by=self.request.user.email,
        )


class MultipleSampleViewSet(viewsets.ModelViewSet):
    queryset = Sample.objects.all()
    serializer_class = MultipleSampleSerializer
    lookup_field = "sample_id"

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user.email,
            last_modified_by=self.request.user.email,
        )


class AllSampleExportViewset(viewsets.ReadOnlyModelViewSet):
    queryset = Sample.objects.all()
    serializer_class = SampleExportSerializer
    lookup_field = "sample_id"

    def get_queryset(self):
        queryset = self.queryset
        patient_id_starts_with = self.request.query_params.get("patient_id_starts_with")
        if patient_id_starts_with is not None:
            queryset = queryset.filter(patient_id__istartswith=patient_id_starts_with)
        return queryset


@login_required(login_url="/login/")
def barcode(request):
    # Returns the page - frontend logic is in the barcode.html template file
    return render(request, "barcode.html")


@login_required(login_url="/login/")
def barcode_samples_used(request):
    return render(request, "barcode-markused.html")


@login_required(login_url="/login/")
def barcode_add_multiple(request):
    return render(request, "barcode-addmultiple.html")


@login_required(login_url="/login/")
def no_timepoint_view(request, study_name):
    """
    Study name options are music, mini_music, marvel and mini_marvel.
    """
    if study_name == "music" or study_name == "mini_music":
        sample_list = Sample.objects.filter(study_name=study_name).filter(music_timepoint=None)
    else:
        sample_list = Sample.objects.filter(study_name=study_name).filter(marvel_timepoint=None)
    sample_count = sample_list.count()
    page = request.GET.get("page", 1)
    paginator = Paginator(sample_list, 1000)
    try:
        samples = paginator.page(page)
    except PageNotAnInteger:
        samples = paginator.page(1)
    except EmptyPage:
        samples = paginator.page(paginator.num_pages)
    context = {
        "sample_list": samples,
        "page_obj": samples,
        "sample_count": sample_count,
    }
    return render(request, "dashboard.html", context)
