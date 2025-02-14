from django.views.generic import ListView

from app.models import DataStore


class DataStoreListView(ListView):
    model = DataStore
    template_name = "datastore/datastore_list.html"
    context_object_name = "datastores"
