import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from app.filters import DataStoreFilter
from app.forms import DataStoreForm, DataStoreUpdateForm
from app.models import DataStore, file_generate_name
from app.services import azure_delete_file, azure_generate_download_link
from app.utils import export_csv

DATASTORE_PAGINATION_SIZE = settings.DATASTORE_PAGINATION_SIZE
User = get_user_model()


@login_required()
@permission_required("app.view_datastore", raise_exception=True)
def datastore_list_view(request):
    datastores = DataStore.objects.all()
    user_access_list = User.objects.filter(groups__name="datastores").order_by("first_name")
    return render(
        request, "datastore/datastore_list.html", {"datastores": datastores, "user_access_list": user_access_list}
    )


@login_required()
@permission_required("app.view_datastore", raise_exception=True)
def datastore_create_view(request):
    if request.method == "POST":
        form = DataStoreForm(request.POST, request.FILES)
        if form.is_valid():
            form.save(commit=False)
            form.instance.file_type = form.cleaned_data["file"].name.split(".")[-1]
            form.instance.original_file_name = form.cleaned_data["file"].name
            if form.cleaned_data["patient_id"]:
                form.instance.patient_id = form.cleaned_data["patient_id"].upper()
                form.instance.formatted_file_name = file_generate_name(
                    form.cleaned_data["file"].name, form.cleaned_data["study_name"], form.cleaned_data["patient_id"]
                )
            else:
                form.instance.formatted_file_name = file_generate_name(
                    form.cleaned_data["file"].name, form.cleaned_data["study_name"]
                )

            form.instance.upload_finished_at = datetime.datetime.now()
            form.instance.uploaded_by = request.user
            form.save()
            return redirect("datastore_list")
        else:
            messages.error(request, "Form is invalid.")
    else:
        form = DataStoreForm()
    return render(request, "datastore/datastore_form.html", {"form": form})


@login_required()
@permission_required("app.view_datastore", raise_exception=True)
def datastore_edit_metadata_view(request, id):
    file = get_object_or_404(DataStore, id=id)
    if request.method == "POST":
        form = DataStoreUpdateForm(request.POST, instance=file)
        if form.is_valid():
            form.save()
            messages.success(request, f"File {file.formatted_file_name} metadata has been updated.")
            return redirect("datastore_list")
        else:
            messages.error(request, "Form is invalid.")
    else:
        form = DataStoreUpdateForm(instance=file)
    return render(request, "datastore/datastore_form_edit.html", {"form": form, "file": file})


@login_required()
@permission_required("app.view_datastore", raise_exception=True)
def datastore_create_view_ajax(request):
    return render(request, "datastore/datastore_form_ajax.html")


@login_required()
@permission_required("app.view_datastore", raise_exception=True)
def datastore_read_view(request, id):
    file = get_object_or_404(DataStore, id=id)
    return render(request, "datastore/datastore_detail.html", {"file": file})


@login_required()
@permission_required("app.view_datastore", raise_exception=True)
def datastore_download_view(request, id):
    file = get_object_or_404(DataStore, id=id)
    download_url = azure_generate_download_link(file, download=True)
    if download_url:
        return redirect(download_url)
    else:
        messages.error(request, "Failed to generate download link.")
        return redirect("datastore_list")


@login_required()
@permission_required("app.view_datastore", raise_exception=True)
def datastore_azure_view(request, id):
    file = get_object_or_404(DataStore, id=id)
    download_url = azure_generate_download_link(file)
    if download_url:
        return redirect(download_url)
    else:
        messages.error(request, "Failed to generate download link.")
        return redirect("datastore_list")


@login_required()
@permission_required("app.view_datastore", raise_exception=True)
def datastore_delete_view(request, id):
    file = get_object_or_404(DataStore, id=id)
    azure_delete_file(file)

    file.delete()
    messages.success(request, "File has been deleted.")
    return redirect("datastore_list")


@login_required()
@permission_required("app.view_datastore", raise_exception=True)
def datastore_search_view(request):
    query_string = ""
    if ("q" in request.GET) and request.GET["q"].strip():
        query_string = request.GET.get("q")
        data_store_list = DataStore.objects.filter(
            Q(patient_id__icontains=query_string)
            | Q(study_name__icontains=query_string)
            | Q(comments__icontains=query_string)
            | Q(category__icontains=query_string)
            | Q(original_file_name__icontains=query_string)
            | Q(formatted_file_name__icontains=query_string)
        )

        return render(
            request, "datastore/datastore_list.html", {"datastores": data_store_list, "query_string": query_string}
        )
    else:
        return redirect("datastore_list")


@login_required()
@permission_required("app.view_datastore", raise_exception=True)
def datastore_filter_view(request):
    queryset = DataStore.objects.all()
    datastore_filter = DataStoreFilter(request.GET, queryset=queryset)
    datastore_list = datastore_filter.qs

    # Pagination
    page = request.GET.get("page", 1)
    paginator = Paginator(datastore_list, DATASTORE_PAGINATION_SIZE)
    try:
        datastores = paginator.page(page)
    except PageNotAnInteger:
        datastores = paginator.page(1)
    except EmptyPage:
        datastores = paginator.page(paginator.num_pages)

    # Allows paginator to reconstruct the initial query string
    parameter_string = ""
    for i in request.GET:
        if i != "page":
            val = request.GET.get(i)
            parameter_string += f"&{i}={val}"

    context = {
        "datastores": datastores,
        "datastore_filter": datastore_filter,
        "parameter_string": parameter_string,
    }
    return render(request, "datastore/datastore_filter.html", context)


@login_required()
@permission_required("app.view_datastore", raise_exception=True)
def datastore_search_export_csv(request):
    query_string = ""
    if ("q" in request.GET) and request.GET["q"].strip():
        query_string = request.GET.get("q")
        queryset = DataStore.objects.filter(
            Q(patient_id__icontains=query_string)
            | Q(study_name__icontains=query_string)
            | Q(comments__icontains=query_string)
            | Q(category__icontains=query_string)
            | Q(original_file_name__icontains=query_string)
            | Q(formatted_file_name__icontains=query_string)
        )
    else:
        queryset = DataStore.objects.all()
    return export_csv(queryset, file_prefix="gtrac", file_name="files")


@login_required()
@permission_required("app.view_datastore", raise_exception=True)
def datastore_filter_export_csv(request):
    queryset = DataStore.objects.all()
    datastore_filter = DataStoreFilter(request.GET, queryset=queryset)
    datastore_list = datastore_filter.qs
    return export_csv(datastore_list, file_prefix="filtered", file_name="files")
