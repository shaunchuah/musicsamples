from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from app.filters import SampleFilter
from app.forms import CheckoutForm, ReactivateForm, SampleForm, UsedForm
from app.models import Sample
from app.services import get_samples_with_clinical_data
from app.utils import (
    export_csv,
    historical_changes,
)

# from django.views.decorators.cache import cache_page


User = get_user_model()

SAMPLE_PAGINATION_SIZE = settings.SAMPLE_PAGINATION_SIZE


@login_required(login_url="/login/")
def index(request):
    # Home Page
    sample_list = get_samples_with_clinical_data(
        Sample.objects.filter(is_used=False).select_related("study_id").order_by("-sample_datetime")
    )
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
    return render(request, "samples/sample_list.html", context)


@login_required(login_url="/login/")
def filter(request):
    queryset = Sample.objects.select_related("study_id").all()
    sample_filter = SampleFilter(request.GET, queryset=queryset)
    sample_list = get_samples_with_clinical_data(sample_filter.qs)
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
        "page_obj": samples,
        "sample_count": sample_count,
        "sample_filter": sample_filter,
        "parameter_string": parameter_string,
    }
    return render(request, "samples/sample_filter.html", context)


@login_required(login_url="/login/")
def filter_export_csv(request):
    queryset = Sample.objects.select_related("study_id").all()
    sample_filter = SampleFilter(request.GET, queryset=queryset)
    sample_list = sample_filter.qs
    return export_csv(sample_list)


@login_required(login_url="/login/")
def used_samples(request):
    queryset = Sample.objects.filter(is_used=True).select_related("study_id").order_by("-last_modified")
    sample_list = get_samples_with_clinical_data(queryset)
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
        sample_list = (
            Sample.objects.filter(is_used=True)
            .filter(
                Q(sample_id__icontains=query_string)
                | Q(study_id__name__icontains=query_string)
                | Q(sample_location__icontains=query_string)
                | Q(sample_sublocation__icontains=query_string)
                | Q(sample_type__icontains=query_string)
                | Q(sample_comments__icontains=query_string)
            )
            .select_related("study_id")
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
    sample_list = Sample.objects.filter(is_used=True).exclude(sample_location="used").select_related("study_id")

    number_of_samples = sample_list.count()
    if number_of_samples == 0:  # if no samples need updating; skip the database update step
        messages.error(request, "No samples to update.")
    else:
        for sample in sample_list:
            sample.sample_location = "used"
            sample.sample_sublocation = ""
            sample.save()
        messages.success(
            request,
            f"Used samples locations archived successfully. ({number_of_samples} samples updated)",
        )
    return redirect(reverse("used_samples"))


@login_required(login_url="/login/")
def account(request):
    # User account page showing last 20 recently accessed samples
    sample_list = (
        Sample.objects.filter(last_modified_by=request.user.email)
        .select_related("study_id")
        .order_by("-last_modified")[:20]
    )
    context = {"sample_list": sample_list}
    return render(request, "samples/account.html", context)


@login_required(login_url="/login/")
def management(request):
    users = User.objects.all()
    user_email_list = []
    for user in users:
        user_email_list.append(user.email)
    user_email_list = ";".join(user_email_list)
    context = {"user_email_list": user_email_list}
    return render(request, "samples/management.html", context)


@login_required(login_url="/login/")
def sample_add(request):
    # Add new sample page
    if request.method == "POST":
        form = SampleForm(request.POST)
        if form.is_valid():
            sample = form.save(commit=False)
            sample.created_by = request.user.email
            sample.last_modified_by = request.user.email
            sample.save()
            messages.success(request, "Sample registered successfully.")
            return redirect(reverse("sample_add"))
        else:
            messages.error(request, "Form is not valid.")
    else:
        form = SampleForm()
    return render(
        request,
        "samples/sample_add.html",
        {"form": form, "page_title": "Add New Sample"},
    )


@login_required(login_url="/login/")
def sample_detail(request, pk):
    # retrieves sample history and also linked notes both public and private
    sample = get_object_or_404(Sample, pk=pk)
    sample_history = sample.history.filter(id=pk)  # type:ignore
    changes = historical_changes(sample_history)
    first_change = sample_history.first()
    processing_time = None
    if sample.processing_datetime is not None:
        time_difference = sample.processing_datetime - sample.sample_datetime
        processing_time = int(time_difference.total_seconds() / 60)
    return render(
        request,
        "samples/sample_detail.html",
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
            sample.last_modified_by = request.user.email
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
        "samples/sample_add.html",
        {"form": form, "page_title": "Update Sample"},
    )


@login_required(login_url="/login/")
def sample_search(request):
    # Sample search in home page
    query_string = ""
    if ("q" in request.GET) and request.GET["q"].strip():
        query_string = request.GET.get("q")

        queryset = (
            Sample.objects.filter(
                Q(sample_id__icontains=query_string)
                | Q(study_id__name__icontains=query_string)
                | Q(sample_location__icontains=query_string)
                | Q(sample_sublocation__icontains=query_string)
                | Q(sample_type__icontains=query_string)
                | Q(sample_comments__icontains=query_string)
            )
            .filter(is_used=False)
            .select_related("study_id")
        )

        if ("include_used_samples" in request.GET) and request.GET["include_used_samples"].strip():
            queryset = Sample.objects.filter(
                Q(sample_id__icontains=query_string)
                | Q(study_id__name__icontains=query_string)
                | Q(sample_location__icontains=query_string)
                | Q(sample_sublocation__icontains=query_string)
                | Q(sample_type__icontains=query_string)
                | Q(sample_comments__icontains=query_string)
            )

        sample_list = get_samples_with_clinical_data(queryset)

        sample_count = sample_list.count()
        return render(
            request,
            "samples/sample_list.html",
            {
                "query_string": query_string,
                "sample_list": sample_list,
                "sample_count": sample_count,
            },
        )
    else:
        return render(request, "samples/sample_list.html", {"query_string": "Null", "sample_count": 0})


@login_required(login_url="/login/")
def sample_checkout(request, pk):
    # Sample Checkout - Quick update of sample location from home page
    sample = get_object_or_404(Sample, pk=pk)
    if request.method == "POST":
        form = CheckoutForm(request.POST, instance=sample)
        if form.is_valid():
            sample = form.save(commit=False)
            sample.last_modified_by = request.user.email
            sample.save()
            messages.success(request, "Sample updated successfully.")
            next_url = request.GET.get("next")
            if next_url:
                return redirect(next_url)
            else:
                return redirect("/")
    else:
        form = CheckoutForm(instance=sample)
    return render(request, "samples/sample_checkout.html", {"form": form})


@login_required(login_url="/login/")
def sample_used(request, pk):
    # Mark sample as used
    sample = get_object_or_404(Sample, pk=pk)
    if request.method == "POST":
        form = UsedForm(request.POST, instance=sample)
        if form.is_valid():
            sample = form.save(commit=False)
            sample.last_modified_by = request.user.email
            sample.save()
            messages.success(request, "Sample marked as used.")
            next_url = request.GET.get("next")
            if next_url:
                return redirect(next_url)
            else:
                return redirect("/")
    else:
        form = UsedForm(instance=sample)
    return render(request, "samples/sample_used.html", {"form": form})


@login_required(login_url="/login/")
def reactivate_sample(request, pk):
    # Reactive sample which has been marked as used
    sample = get_object_or_404(Sample, pk=pk)
    if request.method == "POST":
        form = ReactivateForm(request.POST, instance=sample)
        if form.is_valid():
            sample = form.save(commit=False)
            sample.last_modified_by = request.user.email
            sample.save()
            messages.success(request, "Sample restored.")
            next_url = request.GET.get("next")
            if next_url:
                return redirect(next_url)
            else:
                return redirect("/")
    else:
        form = ReactivateForm(instance=sample)
    return render(request, "samples/sample_reactivate.html", {"form": form})
