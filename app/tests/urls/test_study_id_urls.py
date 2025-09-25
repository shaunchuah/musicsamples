from django.urls import resolve, reverse

from app import views


STUDY_ID_CASES = [
    ("study_id_list", {}, views.study_id_list_view),
    ("study_id_edit", {"name": "test"}, views.study_id_edit_view),
    ("study_id_search", {}, views.study_id_search_view),
    ("study_id_delete", {"id": 1}, views.study_id_delete_view),
    ("study_id_detail", {"name": "test"}, views.study_id_detail_view),
]


def test_study_id_urls_resolve():
    for name, kwargs, view in STUDY_ID_CASES:
        resolved = resolve(reverse(name, kwargs=kwargs) if kwargs else reverse(name))
        assert resolved.func is view
