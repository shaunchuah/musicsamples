import pytest
from django.urls import resolve, reverse

from app import views


@pytest.mark.parametrize(
    ("name", "kwargs", "expected"),
    [
        ("home", {}, views.index),
        ("analytics", {}, views.analytics),
        ("sample_types_pivot", {"study_name": "mini_music"}, views.sample_types_pivot),
        ("account", {}, views.account),
        ("data_export", {}, views.data_export),
        ("management", {}, views.management),
        ("export_users", {}, views.export_users),
        ("export_samples", {}, views.export_samples),
        ("export_historical_samples", {}, views.export_historical_samples),
    ],
)
def test_core_view_urls(name, kwargs, expected):
    resolved = resolve(reverse(name, kwargs=kwargs) if kwargs else reverse(name))
    assert resolved.func is expected
