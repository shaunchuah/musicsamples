from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.edit import CreateView

from app.forms import DataStoreForm
from app.models import DataStore


class DataStoreListView(ListView):
    model = DataStore
    template_name = "datastore/datastore_list.html"
    context_object_name = "datastores"


class DataStoreCreateView(CreateView):
    model = DataStore
    form_class = DataStoreForm
    template_name = "datastore/datastore_form.html"
    success_url = reverse_lazy("datastore_list")
