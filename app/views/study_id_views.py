import pandas as pd
from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from app.forms import StudyIdUpdateForm
from app.models import StudyIdentifier
from app.services import StudyIdentifierImportService
from app.utils import historical_changes

STUDY_ID_PAGINATION_SIZE = settings.STUDY_ID_PAGINATION_SIZE


@api_view(["POST"])
@permission_classes([IsAdminUser])  # Restrict to admins
def import_study_identifiers(request):
    """
    API endpoint to import study identifiers from JSON or CSV data.
    Needs json_data in request.data or csv_file in request.FILES.

    The Data needs the following 6 columns:
    - study_id
    - study_name
    - study_center
    - study_group
    - age
    - sex
    """
    try:
        # If sending JSON data
        if "json_data" in request.data:
            json_data = request.data["json_data"]
            # Handle case where json_data might be a string
            if isinstance(json_data, str):
                import json

                try:
                    json_data = json.loads(json_data)
                except json.JSONDecodeError as e:
                    return Response({"error": f"Invalid JSON format: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

            # Ensure json_data is a list of dictionaries
            if not isinstance(json_data, list):
                return Response({"error": "JSON data must be an array of objects"}, status=status.HTTP_400_BAD_REQUEST)

            df = pd.DataFrame(json_data)
        # If sending a CSV file
        elif "csv_file" in request.FILES:
            df = pd.read_csv(request.FILES["csv_file"])
        else:
            return Response(
                {"error": "No data provided. Send either json_data or csv_file."}, status=status.HTTP_400_BAD_REQUEST
            )

        # Validate the data has required columns
        required_columns = ["study_id", "study_name", "study_center", "study_group", "age", "sex"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return Response(
                {"error": f"Missing required columns: {', '.join(missing_columns)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Process the data
        result = StudyIdentifierImportService.import_from_dataframe(df)

        return Response(result, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": f"Error processing data: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@staff_member_required
def study_id_list_view(request):
    # Get all StudyIdentifiers with related samples and files in a single query
    study_id_list = StudyIdentifier.objects.all().prefetch_related("samples", "files")
    study_id_list_count = study_id_list.count()

    page = request.GET.get("page", 1)
    paginator = Paginator(study_id_list, STUDY_ID_PAGINATION_SIZE)
    try:
        study_id_list = paginator.page(page)
    except PageNotAnInteger:
        study_id_list = paginator.page(1)
    except EmptyPage:
        study_id_list = paginator.page(paginator.num_pages)

    return render(
        request,
        "study_id/study_id_list.html",
        {"study_id_list": study_id_list, "page_obj": study_id_list, "study_id_list_count": study_id_list_count},
    )


@staff_member_required
def study_id_edit_view(request, name: str):
    study_id = StudyIdentifier.objects.get(name=name)

    if request.method == "POST":
        form = StudyIdUpdateForm(request.POST, instance=study_id)
        if form.is_valid():
            form.save()
            return redirect(reverse("study_id_detail", args=[name]))
    else:
        form = StudyIdUpdateForm(instance=study_id)

    return render(request, "study_id/study_id_form.html", {"form": form, "study_id": study_id})


@staff_member_required
def study_id_search_view(request):
    # Sample search in home page
    query_string = ""
    if ("q" in request.GET) and request.GET["q"].strip():
        query_string = request.GET.get("q")

        study_id_list = StudyIdentifier.objects.filter(Q(name__icontains=query_string)).prefetch_related(
            "samples", "files"
        )

        study_id_list_count = study_id_list.count()

        page = request.GET.get("page", 1)
        paginator = Paginator(study_id_list, STUDY_ID_PAGINATION_SIZE)
        try:
            study_id_list = paginator.page(page)
        except PageNotAnInteger:
            study_id_list = paginator.page(1)
        except EmptyPage:
            study_id_list = paginator.page(paginator.num_pages)

        return render(
            request,
            "study_id/study_id_list.html",
            {"study_id_list": study_id_list, "page_obj": study_id_list, "study_id_list_count": study_id_list_count},
        )
    else:
        return render(
            request,
            "study_id/study_id_list.html",
            {"query_string": "Null", "study_id_list_count": study_id_list_count},
        )


@staff_member_required
def study_id_delete_view(request, id):
    study_id = get_object_or_404(StudyIdentifier, id=id)
    try:
        study_id.delete()
        messages.success(request, "Study ID has been deleted.")
        return redirect("study_id_list")
    except Exception as e:
        messages.error(request, f"Failed to delete study ID. {e}")
        return redirect("study_id_list")


@login_required
def study_id_detail_view(request, name):
    # retrieves sample history and also linked notes both public and private
    study_id = get_object_or_404(StudyIdentifier, name=name)
    study_id_history = study_id.history.filter(name=name)
    changes = historical_changes(study_id_history)
    first_change = study_id_history.first()
    return render(
        request,
        "study_id/study_id_detail.html",
        {
            "study_id": study_id,
            "changes": changes,
            "first": first_change,
        },
    )
