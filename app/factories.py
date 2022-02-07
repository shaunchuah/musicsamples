from datetime import timezone
from random import choice

from factory import Faker, LazyAttribute
from factory.django import DjangoModelFactory

from app.choices import SAMPLE_TYPE_CHOICES
from app.models import Sample

LOCATION_CHOICES = ["CIR Freezer", "WGH Endoscopy Freezer", "GGH CRF", "Lab C2.25"]


class SampleFactory(DjangoModelFactory):
    class Meta:
        model = Sample

    sample_id = Faker("ean8")
    patient_id = Faker("ean8")
    sample_location = LazyAttribute(lambda x: choice(LOCATION_CHOICES))
    sample_type = LazyAttribute(lambda x: choice(SAMPLE_TYPE_CHOICES)[1])
    sample_datetime = Faker("date_time_this_year", tzinfo=timezone.utc)
    created_by = Faker("email")
    last_modified_by = Faker("email")
