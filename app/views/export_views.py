from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render

from app.models import Sample
from app.utils import export_csv, queryset_by_study_name

User = get_user_model()


@login_required(login_url="/login/")
def data_export(request):
    return render(request, "export/data_export.html")


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
