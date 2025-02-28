import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Count, Q
from django.db.models.functions import Trunc
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from app.filters import SampleFilter
from app.forms import CheckoutForm, ReactivateForm, SampleForm, UsedForm
from app.models import Sample
from app.utils import (
    create_sample_type_pivot,
    export_csv,
    queryset_by_study_name,
    render_dataframe_to_csv_response,
)
from datasets.models import DatasetAnalytics

# from django.views.decorators.cache import cache_page


User = get_user_model()

SAMPLE_PAGINATION_SIZE = settings.SAMPLE_PAGINATION_SIZE


@login_required(login_url="/login/")
def index(request):
    # Home Page
    sample_list = Sample.objects.filter(is_used=False).select_related("study_id").order_by("-sample_datetime")
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
    sample_list = Sample.objects.filter(is_used=True).select_related("study_id").order_by("-last_modified")
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
# @cache_page(60 * 10)  # Cache page for 10 minutes
def analytics(request):
    # Analytics Page

    # Get last 12 months date
    current_date = datetime.datetime.now(datetime.timezone.utc)
    months_ago = 12
    twelve_months_previous_date = current_date - datetime.timedelta(days=(months_ago * 365 / 12))

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
        Sample.objects.filter(is_used=False).order_by().values("sample_type").annotate(sample_type_count=Count("id"))
    )
    samples_by_study = list(
        Sample.objects.all().order_by().values("study_name").annotate(study_name_count=Count("id"))
    )
    samples_by_location = (
        Sample.objects.filter(is_used=False)
        .values("sample_location")
        .annotate(sample_location_count=Count("id"))
        .order_by("-sample_location_count")
    )

    # GI-DAMPs analytics
    try:
        gidamps_participants_by_center = DatasetAnalytics.objects.get(name="gidamps_participants_by_center").data
        gidamps_participants_by_study_group = DatasetAnalytics.objects.get(
            name="gidamps_participants_by_study_group"
        ).data
        gidamps_participants_by_recruitment_setting = DatasetAnalytics.objects.get(
            name="gidamps_participants_by_recruitment_setting"
        ).data
        gidamps_participants_by_new_diagnosis_of_ibd = DatasetAnalytics.objects.get(
            name="gidamps_participants_by_new_diagnosis_of_ibd"
        ).data
        gidamps_montreal_classification = DatasetAnalytics.objects.get(name="gidamps_montreal_classification").data
    except DatasetAnalytics.DoesNotExist:
        gidamps_participants_by_center = None
        gidamps_participants_by_study_group = None
        gidamps_participants_by_recruitment_setting = None
        gidamps_participants_by_new_diagnosis_of_ibd = None
        gidamps_montreal_classification = None

    context = {
        "total_samples": total_samples,
        "samples_by_month": samples_by_month,
        "samples_by_study": samples_by_study,
        "samples_by_type": samples_by_type,
        "samples_by_location": samples_by_location,
        "total_active_samples": total_active_samples,
        "gidamps_participants_by_center": gidamps_participants_by_center,
        "gidamps_participants_by_study_group": gidamps_participants_by_study_group,
        "gidamps_participants_by_recruitment_setting": gidamps_participants_by_recruitment_setting,
        "gidamps_participants_by_new_diagnosis_of_ibd": gidamps_participants_by_new_diagnosis_of_ibd,
        "gidamps_montreal_classification": gidamps_montreal_classification,
    }
    return render(request, "analytics.html", context)


@login_required(login_url="/login/")
def sample_types_pivot(request, study_name):
    """
    Takes in a url with study_name being one of the five studies
    and returns a pivot table with sample types as columns,
    study ID and sample date as rows.
    """
    qs = Sample.objects.filter(study_name=study_name).select_related("study_id")
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
    sample_list = (
        Sample.objects.filter(last_modified_by=request.user.email)
        .select_related("study_id")
        .order_by("-last_modified")[:20]
    )
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

                # Process each change to use string representation for foreign keys
                for change in delta.changes:
                    # Check if the field is 'study_id' (or any other FK field you want to handle)
                    if change.field == "study_id":
                        # If values aren't None, replace with string representation
                        if change.old is not None:
                            # Get the related model instance from historical record
                            try:
                                from app.models import StudyIdentifier

                                old_instance = StudyIdentifier.objects.get(pk=change.old)
                                change.old = str(old_instance)
                            except (StudyIdentifier.DoesNotExist, ValueError):
                                pass  # Keep as is if we can't find the object

                        if change.new is not None:
                            try:
                                from app.models import StudyIdentifier

                                new_instance = StudyIdentifier.objects.get(pk=change.new)
                                change.new = str(new_instance)
                            except (StudyIdentifier.DoesNotExist, ValueError):
                                pass  # Keep as is if we can't find the object

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
        "samples/sample-add.html",
        {"form": form, "page_title": "Update Sample"},
    )


@login_required(login_url="/login/")
def sample_search(request):
    # Sample search in home page
    query_string = ""
    if ("q" in request.GET) and request.GET["q"].strip():
        query_string = request.GET.get("q")

        sample_list = (
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
            sample_list = Sample.objects.filter(
                Q(sample_id__icontains=query_string)
                | Q(study_id__name__icontains=query_string)
                | Q(sample_location__icontains=query_string)
                | Q(sample_sublocation__icontains=query_string)
                | Q(sample_type__icontains=query_string)
                | Q(sample_comments__icontains=query_string)
            )

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
    return render(request, "samples/sample-checkout.html", {"form": form})


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
    return render(request, "samples/sample-used.html", {"form": form})


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
            | Q(study_id__name__icontains=query_string)
            | Q(sample_location__icontains=query_string)
            | Q(sample_type__icontains=query_string)
            | Q(sample_comments__icontains=query_string)
        ).select_related("study_id")
    else:
        samples_queryset = queryset
    response = export_csv(samples_queryset)
    return response


@login_required(login_url="/login/")
def export_users(request):
    queryset = User.objects.all()
    return export_csv(queryset, file_prefix="users")


@login_required(login_url="/login/")
def export_samples(request):
    queryset = Sample.objects.all()
    return export_csv(queryset, file_prefix="samples")


@login_required(login_url="/login/")
def export_historical_samples(request):
    queryset = Sample.history.all()
    return export_csv(queryset, file_prefix="historicalsamples")
