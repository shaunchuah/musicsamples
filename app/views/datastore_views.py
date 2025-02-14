from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView

from app.forms import DataStoreForm
from app.models import DataStore
from app.services import azure_generate_download_link


class DataStoreListView(ListView):
    model = DataStore
    template_name = "datastore/datastore_list.html"
    context_object_name = "datastores"


def datastore_create_view(request):
    if request.method == "POST":
        form = DataStoreForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("datastore_list")
        else:
            messages.error(request, "Form is invalid.")
    else:
        form = DataStoreForm()
    return render(request, "datastore/datastore_form.html", {"form": form})


def datastore_download_view(request, id):
    file = get_object_or_404(DataStore, id=id)
    download_url = azure_generate_download_link(file)
    if download_url:
        return redirect(download_url)
    else:
        messages.error(request, "Failed to generate download link.")
        return redirect("datastore_list")
