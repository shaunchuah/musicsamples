from datetime import timezone
from random import choice

from factory import Faker, LazyAttribute, Sequence
from factory.django import DjangoModelFactory

from app.models import Sample

LOCATION_CHOICES = ["CIR Freezer", "WGH Endoscopy Freezer", "GGH CRF", "Lab C2.25"]
SAMPLE_TYPE_CHOICES = [
    "PaxGene ccfDNA tube",
    "Standard EDTA tube",
    "Stool",
    "Saliva",
    "PaxGene ccfDNA plasma child aliquot",
    "Calprotectin",
    "qFIT",
]


class SampleFactory(DjangoModelFactory):
    class Meta:
        model = Sample

    sample_id = Sequence(lambda n: "DEMO-%05d" % n)
    patient_id = Sequence(lambda n: "DEMO-%d" % n)
    sample_location = LazyAttribute(lambda x: choice(LOCATION_CHOICES))
    sample_type = LazyAttribute(lambda x: choice(SAMPLE_TYPE_CHOICES))
    sample_datetime = Faker("date_time_this_year", tzinfo=timezone.utc)
    created_by = Faker("email")
    last_modified_by = Faker("email")
