from random import choice
from app.models import Sample
from app.choices import SAMPLE_TYPE_CHOICES
from factory import Faker, LazyAttribute
from factory.django import DjangoModelFactory

LOCATION_CHOICES = ["CIR Freezer", "WGH Endoscopy Freezer", "GGH CRF", "Lab C2.25"]


class SampleFactory(DjangoModelFactory):
    class Meta:
        model = Sample

    sample_id = "MGM" + str(Faker("barcode"))
    patient_id = "GID-" + str(Faker("barcode"))
    sample_location = LazyAttribute(lambda x: choice(LOCATION_CHOICES))
    sample_type = LazyAttribute(lambda x: choice(SAMPLE_TYPE_CHOICES)[1])
    sample_datetime = Faker("date_time_this_year")
    created_by = Faker("email")
    last_modified_by = Faker("email")
