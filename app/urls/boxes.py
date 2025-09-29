from django.urls import path

from ..views.box_views import (
    BasicScienceBoxCreateView,
    BasicScienceBoxDeleteView,
    BasicScienceBoxDetailView,
    BasicScienceBoxListView,
    BasicScienceBoxUpdateView,
    ExperimentCreateView,
    ExperimentDeleteView,
    ExperimentDetailView,
    ExperimentListView,
    ExperimentRestoreView,
    ExperimentUpdateView,
    box_filter,
    box_filter_export_csv,
    box_search,
    create_experiment,
    experiment_filter,
    experiment_filter_export_csv,
    experiment_search,
    export_boxes_csv,
    export_experiments_csv,
)

app_name = "boxes"

urlpatterns = [
    path("", BasicScienceBoxListView.as_view(), name="list"),
    path("filter/", box_filter, name="filter"),
    path("filter/export_csv/", box_filter_export_csv, name="filter_export_csv"),
    path("create/", BasicScienceBoxCreateView.as_view(), name="create"),
    path("view/<int:pk>/", BasicScienceBoxDetailView.as_view(), name="detail"),
    path("edit/<int:pk>/", BasicScienceBoxUpdateView.as_view(), name="edit"),
    path("delete/<int:pk>/", BasicScienceBoxDeleteView.as_view(), name="delete"),
    path("search/", box_search, name="search"),
    path("create-experiment/", create_experiment, name="create_experiment"),
    path("export_csv/", export_boxes_csv, name="export_csv"),
    path("experiments/", ExperimentListView.as_view(), name="experiment_list"),
    path("experiments/create/", ExperimentCreateView.as_view(), name="experiment_create"),
    path("experiments/view/<int:pk>/", ExperimentDetailView.as_view(), name="experiment_detail"),
    path("experiments/edit/<int:pk>/", ExperimentUpdateView.as_view(), name="experiment_edit"),
    path("experiments/delete/<int:pk>/", ExperimentDeleteView.as_view(), name="experiment_delete"),
    path("experiments/restore/<int:pk>/", ExperimentRestoreView.as_view(), name="experiment_restore"),
    path("experiments/search/", experiment_search, name="experiment_search"),
    path("experiments/export_csv/", export_experiments_csv, name="experiment_export_csv"),
    path("experiments/filter/", experiment_filter, name="experiment_filter"),
    path(
        "experiments/filter/export_csv/",
        experiment_filter_export_csv,
        name="experiment_filter_export_csv",
    ),
]
