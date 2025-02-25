from datetime import timezone
from random import choice

from factory import Faker, LazyAttribute, Sequence, SubFactory
from factory.django import DjangoModelFactory

from app.choices import SampleTypeChoices, StudyNameChoices
from app.models import Sample, StudyIdentifier

LOCATION_CHOICES = ["CIR Freezer", "WGH Endoscopy Freezer", "GGH CRF", "Lab C2.25"]


class StudyIdentifierFactory(DjangoModelFactory):
    class Meta:
        model = StudyIdentifier

    name = Sequence(lambda n: "DEMO-%d" % n)
    study_name = LazyAttribute(lambda x: choice(StudyNameChoices.values))


class SampleFactory(DjangoModelFactory):
    class Meta:
        model = Sample

    study_name = LazyAttribute(lambda x: choice(StudyNameChoices.values))
    sample_id = Sequence(lambda n: "DEMO-%05d" % n)
    study_id = SubFactory(StudyIdentifierFactory)
    sample_location = LazyAttribute(lambda x: choice(LOCATION_CHOICES))
    sample_type = LazyAttribute(lambda x: choice(SampleTypeChoices.values))
    sample_datetime = Faker("date_time_this_year", tzinfo=timezone.utc)
    created_by = Faker("email")
    last_modified_by = Faker("email")
