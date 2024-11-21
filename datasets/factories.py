from factory import Faker
from factory.django import DjangoModelFactory

from app.choices import StudyNameChoices
from datasets.models import Dataset


class DatasetFactory(DjangoModelFactory):
    class Meta:
        model = Dataset

    study_name = Faker("random_element", elements=StudyNameChoices.values)
    name = Faker("word")
    description = Faker("sentence")
    json = Faker("json")
