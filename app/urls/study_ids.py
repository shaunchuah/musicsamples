from django.urls import path

from .. import views

urlpatterns = [
    path("study_id/", views.study_id_list_view, name="study_id_list"),
    path("study_id/edit/<str:name>/", views.study_id_edit_view, name="study_id_edit"),
    path("study_id/search/", views.study_id_search_view, name="study_id_search"),
    path("study_id/delete/<int:id>/", views.study_id_delete_view, name="study_id_delete"),
    path("study_id/detail/<str:name>/", views.study_id_detail_view, name="study_id_detail"),
]
