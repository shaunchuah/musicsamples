from django.urls import path

from .views.box_views import (
    BasicScienceBoxCreateView,
    BasicScienceBoxDeleteView,
    BasicScienceBoxListView,
    BasicScienceBoxUpdateView,
    box_search,
)

app_name = "boxes"

urlpatterns = [
    path("", BasicScienceBoxListView.as_view(), name="list"),
    path("create/", BasicScienceBoxCreateView.as_view(), name="create"),
    path("<int:pk>/edit/", BasicScienceBoxUpdateView.as_view(), name="edit"),
    path("<int:pk>/delete/", BasicScienceBoxDeleteView.as_view(), name="delete"),
    path("search/", box_search, name="search"),
]
