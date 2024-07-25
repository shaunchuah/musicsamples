import datetime

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Count, Q
from django.db.models.functions import Trunc
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from rest_framework import viewsets

from app.filters import SampleFilter
from app.forms import CheckoutForm, ReactivateForm, SampleForm, UsedForm
from app.models import Sample
from app.serializers import (
    MultipleSampleSerializer,
    SampleExportSerializer,
    SampleIsUsedSerializer,
    SampleSerializer,
)
from app.utils import (
    create_sample_type_pivot,
    export_csv,
    queryset_by_study_name,
    render_dataframe_to_csv_response,
)

# from django.views.decorators.cache import cache_page


User = get_user_model()

SAMPLE_PAGINATION_SIZE = 100


@login_required(login_url="/login/")
def index(request):
    # Home Page
    sample_list = Sample.objects.filter(is_used=False).order_by("-sample_datetime")
    sample_count = sample_list.count()
    page = request.GET.get("page", 1)
    paginator = Paginator(sample_list, SAMPLE_PAGINATION_SIZE)
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
    return render(request, "index.html", context)


@login_required(login_url="/login/")
def filter(request):
    queryset = Sample.objects.all()
    sample_filter = SampleFilter(request.GET, queryset=queryset)
    sample_list = sample_filter.qs
    sample_count = sample_list.count()

    # Pagination
    page = request.GET.get("page", 1)
    paginator = Paginator(sample_list, SAMPLE_PAGINATION_SIZE)
    try:
        samples = paginator.page(page)
    except PageNotAnInteger:
        samples = paginator.page(1)
    except EmptyPage:
        samples = paginator.page(paginator.num_pages)

    # Allows paginator to reconstruct the initial query string
    parameter_string = ""
    for i in request.GET:
        if i != "page":
            val = request.GET.get(i)
            parameter_string += f"&{i}={val}"

    context = {
        "sample_list": samples,
        "sample_count": sample_count,
        "sample_filter": sample_filter,
        "parameter_string": parameter_string,
    }
    return render(request, "filter.html", context)


@login_required(login_url="/login/")
def filter_export_csv(request):
    queryset = Sample.objects.all()
    sample_filter = SampleFilter(request.GET, queryset=queryset)
    sample_list = sample_filter.qs
    return export_csv(sample_list)


@login_required(login_url="/login/")
def used_samples(request):
    sample_list = Sample.objects.filter(is_used=True).order_by("-last_modified")
    sample_count = sample_list.count()
    page = request.GET.get("page", 1)
    paginator = Paginator(sample_list, SAMPLE_PAGINATION_SIZE)
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
    return render(request, "samples/used_samples.html", context)


@login_required(login_url="/login/")
def used_samples_search(request):
    query_string = ""
    if ("q" in request.GET) and request.GET["q"].strip():
        query_string = request.GET.get("q")
        sample_list = Sample.objects.filter(is_used=True).filter(
            Q(sample_id__icontains=query_string)
            | Q(patient_id__icontains=query_string)
            | Q(sample_location__icontains=query_string)
            | Q(sample_sublocation__icontains=query_string)
            | Q(sample_type__icontains=query_string)
            | Q(sample_comments__icontains=query_string)
        )
        sample_count = sample_list.count()
        return render(
            request,
            "samples/used_samples.html",
            {
                "query_string": query_string,
                "sample_list": sample_list,
                "sample_count": sample_count,
            },
        )
    else:
        return render(
            request,
            "samples/used_samples.html",
            {"query_string": "Null", "sample_count": 0},
        )


@login_required(login_url="/login/")
def used_samples_archive_all(request):
    """
    This function will retrieve all used samples and remove their last location.
    This helps to keep the database clean.
    """
    sample_list = Sample.objects.filter(is_used=True).exclude(sample_location="used")

    number_of_samples = sample_list.count()
    if (
        number_of_samples == 0
    ):  # if no samples need updating; skip the database update step
        messages.error(request, "No samples to update.")
    else:
        for sample in sample_list:
            sample.sample_location = "used"
            sample.sample_sublocation = ""
            sample.save()
        messages.success(
            request,
            "Used samples locations archived successfully."
            f" ({number_of_samples} samples updated)",
        )
    return redirect(reverse("used_samples"))


@login_required(login_url="/login/")
# @cache_page(60 * 10)  # Cache page for 10 minutes
def analytics(request):
    # Analytics Page

    # Get last 12 months date
    current_date = datetime.datetime.now(datetime.timezone.utc)
    months_ago = 12
    twelve_months_previous_date = current_date - datetime.timedelta(
        days=(months_ago * 365 / 12)
    )

    total_samples = Sample.objects.all().count()
    total_active_samples = Sample.objects.all().filter(is_used=False).count()
    samples_by_month = list(
        Sample.objects.filter(sample_datetime__gte=twelve_months_previous_date)
        .order_by()
        .annotate(sample_month=Trunc("sample_datetime", "month"))
        .values("sample_month")
        .annotate(sample_count=Count("id"))
        .order_by("sample_month")
    )

    for item in samples_by_month:
        item["sample_month_label"] = item["sample_month"].strftime("%b %Y")

    samples_by_type = list(
        Sample.objects.filter(is_used=False)
        .order_by()
        .values("sample_type")
        .annotate(sample_type_count=Count("id"))
    )
    samples_by_study = list(
        Sample.objects.all()
        .order_by()
        .values("study_name")
        .annotate(study_name_count=Count("id"))
    )
    samples_by_location = (
        Sample.objects.filter(is_used=False)
        .values("sample_location")
        .annotate(sample_location_count=Count("id"))
        .order_by("-sample_location_count")
    )
    context = {
        "total_samples": total_samples,
        "samples_by_month": samples_by_month,
        "samples_by_study": samples_by_study,
        "samples_by_type": samples_by_type,
        "samples_by_location": samples_by_location,
        "total_active_samples": total_active_samples,
    }
    return render(request, "analytics.html", context)


@login_required(login_url="/login/")
def sample_types_pivot(request, study_name):
    """
    Takes in a url with study_name being one of the five studies
    and returns a pivot table with sample types as columns,
    patient ID and sample date as rows.
    """
    qs = Sample.objects.filter(study_name=study_name)
    output_df = create_sample_type_pivot(qs, study_name=study_name)
    response = render_dataframe_to_csv_response(output_df, study_name=study_name)
    return response


@login_required(login_url="/login/")
def reference(request):
    # Reference static page for publishing lab protocols
    return render(request, "reference.html")


@login_required(login_url="/login/")
def account(request):
    # User account page showing last 20 recently accessed samples
    sample_list = Sample.objects.filter(
        last_modified_by=request.user.username
    ).order_by("-last_modified")[:20]
    context = {"sample_list": sample_list}
    return render(request, "account.html", context)


@login_required(login_url="/login/")
def data_export(request):
    return render(request, "data_export.html")


@login_required(login_url="/login/")
def management(request):
    users = User.objects.all()
    user_email_list = []
    for user in users:
        user_email_list.append(user.email)
    user_email_list = ";".join(user_email_list)
    context = {"user_email_list": user_email_list}
    return render(request, "management.html", context)


@login_required(login_url="/login/")
def sample_add(request):
    # Add mew sample page
    if request.method == "POST":
        form = SampleForm(request.POST)
        if form.is_valid():
            sample = form.save(commit=False)
            sample.created_by = request.user.username
            sample.last_modified_by = request.user.username
            sample.save()
            messages.success(request, "Sample registered successfully.")
            return redirect(reverse("sample_add"))
        else:
            messages.error(request, "Form is not valid.")
    else:
        form = SampleForm()
    return render(
        request,
        "samples/sample-add.html",
        {"form": form, "page_title": "Add New Sample"},
    )


def historical_changes(query):
    # Historical changes integrates simple history into the sample detail page
    changes = []
    if query is not None:
        last = query.first()
        for all_changes in range(query.count()):
            new_record, old_record = last, last.prev_record
            if old_record is not None:
                delta = new_record.diff_against(old_record)
                changes.append(delta)
                last = old_record
        return changes


@login_required(login_url="/login/")
def sample_detail(request, pk):
    # retrieves sample history and also linked notes both public and private
    sample = get_object_or_404(Sample, pk=pk)
    sample_history = sample.history.filter(id=pk)
    changes = historical_changes(sample_history)
    first_change = sample_history.first()
    processing_time = None
    if sample.processing_datetime is not None:
        time_difference = sample.processing_datetime - sample.sample_datetime
        processing_time = int(time_difference.total_seconds() / 60)
    return render(
        request,
        "samples/sample-detail.html",
        {
            "sample": sample,
            "changes": changes,
            "first": first_change,
            "processing_time": processing_time,
        },
    )


@login_required(login_url="/login/")
def sample_edit(request, pk):
    # Sample Edit Page
    sample = get_object_or_404(Sample, pk=pk)
    if request.method == "POST":
        form = SampleForm(request.POST, instance=sample)
        if form.is_valid():
            sample = form.save(commit=False)
            sample.last_modified_by = request.user.username
            sample.save()
            messages.success(request, "Sample updated successfully.")
            next_url = request.GET.get("next")
            if next_url:
                return redirect(next_url)
            else:
                return redirect("/")
    else:
        form = SampleForm(instance=sample)
    return render(
        request,
        "samples/sample-add.html",
        {"form": form, "page_title": "Update Sample"},
    )


@login_required(login_url="/login/")
def sample_search(request):
    # Sample search in home page
    query_string = ""
    if ("q" in request.GET) and request.GET["q"].strip():
        query_string = request.GET.get("q")

        sample_list = Sample.objects.filter(
            Q(sample_id__icontains=query_string)
            | Q(patient_id__icontains=query_string)
            | Q(sample_location__icontains=query_string)
            | Q(sample_sublocation__icontains=query_string)
            | Q(sample_type__icontains=query_string)
            | Q(sample_comments__icontains=query_string)
        ).filter(is_used=False)

        if ("include_used_samples" in request.GET) and request.GET[
            "include_used_samples"
        ].strip():
            sample_list = Sample.objects.filter(
                Q(sample_id__icontains=query_string)
                | Q(patient_id__icontains=query_string)
                | Q(sample_location__icontains=query_string)
                | Q(sample_sublocation__icontains=query_string)
                | Q(sample_type__icontains=query_string)
                | Q(sample_comments__icontains=query_string)
            )

        sample_count = sample_list.count()
        return render(
            request,
            "index.html",
            {
                "query_string": query_string,
                "sample_list": sample_list,
                "sample_count": sample_count,
            },
        )
    else:
        return render(
            request, "index.html", {"query_string": "Null", "sample_count": 0}
        )


@login_required(login_url="/login/")
def sample_checkout(request, pk):
    # Sample Checkout - Quick update of sample location from home page
    sample = get_object_or_404(Sample, pk=pk)
    if request.method == "POST":
        form = CheckoutForm(request.POST, instance=sample)
        if form.is_valid():
            sample = form.save(commit=False)
            sample.last_modified_by = request.user.username
            sample.save()
            messages.success(request, "Sample updated successfully.")
            next_url = request.GET.get("next")
            if next_url:
                return redirect(next_url)
            else:
                return redirect("/")
    else:
        form = CheckoutForm(instance=sample)
    return render(request, "samples/sample-checkout.html", {"form": form})


@login_required(login_url="/login/")
def sample_used(request, pk):
    # Mark sample as used
    sample = get_object_or_404(Sample, pk=pk)
    if request.method == "POST":
        form = UsedForm(request.POST, instance=sample)
        if form.is_valid():
            sample = form.save(commit=False)
            sample.last_modified_by = request.user.username
            sample.save()
            messages.success(request, "Sample marked as used.")
            next_url = request.GET.get("next")
            if next_url:
                return redirect(next_url)
            else:
                return redirect("/")
    else:
        form = UsedForm(instance=sample)
    return render(request, "samples/sample-used.html", {"form": form})


@login_required(login_url="/login/")
def reactivate_sample(request, pk):
    # Reactive sample which has been marked as used
    sample = get_object_or_404(Sample, pk=pk)
    if request.method == "POST":
        form = ReactivateForm(request.POST, instance=sample)
        if form.is_valid():
            sample = form.save(commit=False)
            sample.last_modified_by = request.user.username
            sample.save()
            messages.success(request, "Sample restored.")
            next_url = request.GET.get("next")
            if next_url:
                return redirect(next_url)
            else:
                return redirect("/")
    else:
        form = ReactivateForm(instance=sample)
    return render(request, "samples/sample-reactivate.html", {"form": form})


@login_required(login_url="/login/")
def export_csv_view(request, study_name):
    """
    Takes in study_name parameter and returns csv file with relevant samples.
    Study name options are: music, gidamps, marvel, mini_music
    If no study_name is passed, all samples are exported by default.
    """
    queryset = queryset_by_study_name(Sample, study_name)

    # Exports custom views based on the search string otherwise exports entire database
    query_string = ""
    if ("q" in request.GET) and request.GET["q"].strip():
        query_string = request.GET.get("q")
        samples_queryset = queryset.filter(
            Q(sample_id__icontains=query_string)
            | Q(patient_id__icontains=query_string)
            | Q(sample_location__icontains=query_string)
            | Q(sample_type__icontains=query_string)
            | Q(sample_comments__icontains=query_string)
        )
    else:
        samples_queryset = queryset
    response = export_csv(samples_queryset)
    return response


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
            last_modified_by=self.request.user.username,
        )


class SampleIsUsedViewSet(viewsets.ModelViewSet):
    queryset = Sample.objects.all()
    serializer_class = SampleIsUsedSerializer
    lookup_field = "sample_id"

    def perform_update(self, serializer):
        serializer.save(
            last_modified_by=self.request.user.username,
        )


class MultipleSampleViewSet(viewsets.ModelViewSet):
    queryset = Sample.objects.all()
    serializer_class = MultipleSampleSerializer
    lookup_field = "sample_id"

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user.username,
            last_modified_by=self.request.user.username,
        )


class SampleExportViewset(viewsets.ReadOnlyModelViewSet):
    queryset = Sample.objects.filter(patient_id__startswith="GID")
    serializer_class = SampleExportSerializer
    lookup_field = "sample_id"


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
        sample_list = Sample.objects.filter(study_name=study_name).filter(
            music_timepoint=None
        )
    else:
        sample_list = Sample.objects.filter(study_name=study_name).filter(
            marvel_timepoint=None
        )
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
    return render(request, "index.html", context)
