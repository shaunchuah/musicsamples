from datetime import datetime
from unittest.mock import patch

import pytest
from django.http import HttpResponse

from datasets.utils import export_json_field


@pytest.fixture
def mock_datetime():
    with patch("datetime.datetime") as mock_dt:
        mock_dt.now.return_value = datetime(2023, 1, 1)
        yield mock_dt


@pytest.fixture
def sample_json_data():
    return [
        {"name": "John Doe", "age": 30, "email": "john@example.com"},
        {"name": "Jane Smith", "age": 25, "email": "jane@example.com"},
    ]


def test_basic_export(mock_datetime, sample_json_data):
    response = export_json_field("test_dataset", sample_json_data)

    assert isinstance(response, HttpResponse)
    assert response["Content-Type"] == "text/csv"
    assert response["Content-Disposition"] == 'attachment; filename="test_dataset_2023-01-01.csv"'

    content = response.content.decode("utf-8")
    assert "name,age,email" in content
    assert "John Doe,30,john@example.com" in content
    assert "Jane Smith,25,jane@example.com" in content


def test_empty_json_export(mock_datetime):
    response = export_json_field("empty_dataset", [])

    assert isinstance(response, HttpResponse)
    content = response.content.decode("utf-8").strip()
    assert content == ""


def test_nested_json_export(mock_datetime):
    nested_data = [
        {"user": {"name": "John", "details": {"age": 30}}},
        {"user": {"name": "Jane", "details": {"age": 25}}},
    ]

    response = export_json_field("nested_dataset", nested_data)
    content = response.content.decode("utf-8")

    assert "user.name,user.details.age" in content
    assert "John,30" in content
    assert "Jane,25" in content


def test_mixed_types_export(mock_datetime):
    mixed_data = [
        {"name": "John", "active": True, "score": 9.5, "tags": None},
        {"name": "Jane", "active": False, "score": 8.7, "tags": None},
    ]

    response = export_json_field("mixed_dataset", mixed_data)
    content = response.content.decode("utf-8")

    assert "name,active,score,tags" in content
    assert "John,True,9.5" in content
    assert "Jane,False,8.7" in content


def test_special_chars_dataset_name(mock_datetime, sample_json_data):
    response = export_json_field("test/dataset with spaces!", sample_json_data)

    assert response["Content-Disposition"] == 'attachment; filename="test/dataset with spaces!_2023-01-01.csv"'


def test_single_record_export(mock_datetime):
    single_data = [{"name": "John", "age": 30}]

    response = export_json_field("single_record", single_data)
    content = response.content.decode("utf-8")

    assert "name,age" in content
    assert "John,30" in content
    assert content.count("\n") == 2  # Header + one data row


def test_many_columns_export(mock_datetime):
    wide_data = [{f"col_{i}": i for i in range(100)}]

    response = export_json_field("wide_dataset", wide_data)
    content = response.content.decode("utf-8")
    header = content.split("\n")[0]

    assert len(header.split(",")) == 100
    assert all(f"col_{i}" in header for i in range(100))
