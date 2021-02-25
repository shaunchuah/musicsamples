from django.test import TestCase, SimpleTestCase, Client
from django.db import models
from mixer.backend.django import mixer
import pytest

pytestmark = pytest.mark.django_db

class TestSample:
    def test_model(self):
        obj = mixer.blend('app.Sample')
        assert obj.pk == 1, 'Should create sample instance with primary key id of 1.'
