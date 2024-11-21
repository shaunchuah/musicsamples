import pytest
from django.test import TestCase

from datasets.factories import DatasetFactory

pytestmark = pytest.mark.django_db


class TestDatasetModel(TestCase):
    def test_str_method(self):
        dataset = DatasetFactory(name="test001")
        assert dataset.__str__() == "test001"
