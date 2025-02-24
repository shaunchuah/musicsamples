from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView

from app.filters import DataStoreFilter
from app.forms import DataStoreForm
from app.models import DataStore
from app.services import azure_delete_file, azure_generate_download_link
from app.utils import export_csv

DATASTORE_PAGINATION_SIZE = settings.DATASTORE_PAGINATION_SIZE


class DataStoreListView(LoginRequiredMixin, ListView):
    model = DataStore
    template_name = "datastore/datastore_list.html"
    context_object_name = "datastores"


@login_required()
def datastore_create_view(request):
    if request.method == "POST":
        form = DataStoreForm(request.POST, request.FILES)
        if form.is_valid():
            form.save(commit=False)
            form.instance.uploaded_by = request.user
            form.save()
            return redirect("datastore_list")
        else:
            messages.error(request, "Form is invalid.")
    else:
        form = DataStoreForm()
    return render(request, "datastore/datastore_form.html", {"form": form})


def datastore_read_view(request, id):
    file = get_object_or_404(DataStore, id=id)
    return render(request, "datastore/datastore_detail.html", {"file": file})


@login_required()
def datastore_download_view(request, id):
    file = get_object_or_404(DataStore, id=id)
    download_url = azure_generate_download_link(file, download=True)
    if download_url:
        return redirect(download_url)
    else:
        messages.error(request, "Failed to generate download link.")
        return redirect("datastore_list")


@login_required()
def datastore_azure_view(request, id):
    file = get_object_or_404(DataStore, id=id)
    download_url = azure_generate_download_link(file)
    if download_url:
        return redirect(download_url)
    else:
        messages.error(request, "Failed to generate download link.")
        return redirect("datastore_list")


@login_required()
def datastore_delete_view(request, id):
    file = get_object_or_404(DataStore, id=id)
    azure_delete_file(file)

    file.delete()
    messages.success(request, "File has been deleted.")
    return redirect("datastore_list")


@login_required()
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
def datastore_filter_export_csv(request):
    queryset = DataStore.objects.all()
    datastore_filter = DataStoreFilter(request.GET, queryset=queryset)
    datastore_list = datastore_filter.qs
    return export_csv(datastore_list, file_prefix="filtered", file_name="files")
