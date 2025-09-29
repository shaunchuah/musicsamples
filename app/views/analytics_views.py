import datetime

from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.db.models.functions import Trunc
from django.shortcuts import render

from app.models import Sample
from core.utils.dataframes import create_sample_type_pivot
from core.utils.export import render_dataframe_to_csv_response
from datasets.models import DatasetAnalytics


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
    return render(request, "analytics/analytics.html", context)


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
