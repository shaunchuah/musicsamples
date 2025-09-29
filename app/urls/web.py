from django.urls import path
from django.views.generic.base import TemplateView

from .. import views

urlpatterns = [
    path("", views.index, name="home"),
    path(
        "robots.txt",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
    ),
    path("filter/", views.filter, name="filter"),
    path(
        "filter/export_csv/",
        views.filter_export_csv,
        name="filter_export_csv",
    ),
    path("analytics/", views.analytics, name="analytics"),
    path(
        "analytics/sample_types_pivot/<str:study_name>/",
        views.sample_types_pivot,
        name="sample_types_pivot",
    ),
    path("data_export/", views.data_export, name="data_export"),
]
