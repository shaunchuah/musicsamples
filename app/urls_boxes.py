from django.urls import path

from .views.box_views import (
    BasicScienceBoxCreateView,
    BasicScienceBoxDeleteView,
    BasicScienceBoxDetailView,
    BasicScienceBoxListView,
    BasicScienceBoxUpdateView,
    box_search,
    create_experimental_id,
    export_boxes_csv,
)

app_name = "boxes"

urlpatterns = [
    path("", BasicScienceBoxListView.as_view(), name="list"),
    path("create/", BasicScienceBoxCreateView.as_view(), name="create"),
    path("view/<int:pk>/", BasicScienceBoxDetailView.as_view(), name="detail"),
    path("edit/<int:pk>/", BasicScienceBoxUpdateView.as_view(), name="edit"),
    path("delete/<int:pk>/", BasicScienceBoxDeleteView.as_view(), name="delete"),
    path("search/", box_search, name="search"),
    path("create-experimental-id/", create_experimental_id, name="create_experimental_id"),
    path("export_csv/", export_boxes_csv, name="export_csv"),
]
