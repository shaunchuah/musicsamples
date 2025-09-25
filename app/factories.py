from datetime import timezone
from random import choice

from factory import Faker, LazyAttribute, PostGeneration, Sequence, SubFactory
from factory.django import DjangoModelFactory

from app.choices import (
    BasicScienceBoxTypeChoices,
    BasicScienceGroupChoices,
    BasicScienceSampleTypeChoices,
    ColumnChoices,
    DepthChoices,
    FreezerLocationChoices,
    RowChoices,
    SampleTypeChoices,
    SpeciesChoices,
    StudyNameChoices,
    TissueTypeChoices,
)
from app.models import (
    BasicScienceBox,
    BasicScienceSampleType,
    ExperimentalID,
    Sample,
    StudyIdentifier,
    TissueType,
)
from users.factories import UserFactory

LOCATION_CHOICES = ["CIR Freezer", "WGH Endoscopy Freezer", "GGH CRF", "Lab C2.25"]


class StudyIdentifierFactory(DjangoModelFactory):
    class Meta:  # type:ignore
        model = StudyIdentifier

    name = Sequence(lambda n: "DEMO-%d" % n)
    study_name = LazyAttribute(lambda x: choice(StudyNameChoices.values))


class SampleFactory(DjangoModelFactory):
    class Meta:  # type:ignore
        model = Sample

    study_name = LazyAttribute(lambda x: choice(StudyNameChoices.values))
    sample_id = Sequence(lambda n: "DEMO-%05d" % n)
    study_id = SubFactory(StudyIdentifierFactory)
    sample_location = LazyAttribute(lambda x: choice(LOCATION_CHOICES))
    sample_type = LazyAttribute(lambda x: choice(SampleTypeChoices.values))
    sample_datetime = Faker("date_time_this_year", tzinfo=timezone.utc)
    created_by = Faker("email")
    last_modified_by = Faker("email")


class ExperimentalIDFactory(DjangoModelFactory):
    class Meta:  # type:ignore
        model = ExperimentalID

    basic_science_group = LazyAttribute(lambda x: choice(BasicScienceGroupChoices.values))
    name = Sequence(lambda n: "EXP-%03d" % n)
    description = Faker("sentence")
    date = Faker("date_this_year")
    species = LazyAttribute(lambda x: choice(SpeciesChoices.values))

    @PostGeneration
    def sample_types(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for sample_type in extracted:
                self.sample_types.add(sample_type)  # type:ignore
        else:
            for _ in range(choice([0, 1, 2])):
                sample_type, _ = BasicScienceSampleType.objects.get_or_create(
                    name=list(BasicScienceSampleTypeChoices.values)[
                        choice(range(len(BasicScienceSampleTypeChoices.values)))
                    ],
                    defaults={"label": Faker("word")},
                )
                self.sample_types.add(sample_type)  # type:ignore

    @PostGeneration
    def tissue_types(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for tissue_type in extracted:
                self.tissue_types.add(tissue_type)  # type:ignore
        else:
            if choice([True, False]):
                tissue_type, _ = TissueType.objects.get_or_create(
                    name=list(TissueTypeChoices.values)[choice(range(len(TissueTypeChoices.values)))],
                    defaults={"label": Faker("word")},
                )
                self.tissue_types.add(tissue_type)  # type:ignore


class BasicScienceSampleTypeFactory(DjangoModelFactory):
    class Meta:  # type:ignore
        model = BasicScienceSampleType

    name = Sequence(
        lambda n: list(BasicScienceSampleTypeChoices.values)[n % len(BasicScienceSampleTypeChoices.values)]
    )
    label = Faker("word")

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Override to use get_or_create with defaults for non-unique fields"""
        defaults = {}
        if "label" in kwargs:
            defaults["label"] = kwargs.pop("label")
        return model_class.objects.get_or_create(defaults=defaults, **kwargs)[0]


class TissueTypeFactory(DjangoModelFactory):
    class Meta:  # type:ignore
        model = TissueType

    name = Sequence(lambda n: list(TissueTypeChoices.values)[n % len(TissueTypeChoices.values)])
    label = Faker("word")

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Override to use get_or_create with defaults for non-unique fields"""
        defaults = {}
        if "label" in kwargs:
            defaults["label"] = kwargs.pop("label")
        return model_class.objects.get_or_create(defaults=defaults, **kwargs)[0]


class BasicScienceBoxFactory(DjangoModelFactory):
    class Meta:  # type:ignore
        model = BasicScienceBox

    box_id = Sequence(lambda n: "BOX-%04d" % n)
    box_type = LazyAttribute(lambda x: choice(BasicScienceBoxTypeChoices.values))
    location = LazyAttribute(lambda x: choice(FreezerLocationChoices.values))
    row = LazyAttribute(lambda x: choice(RowChoices.values))
    column = LazyAttribute(lambda x: choice(ColumnChoices.values))
    depth = LazyAttribute(lambda x: choice(DepthChoices.values))
    comments = Faker("sentence")
    is_used = False
    created_by = SubFactory(UserFactory)
    last_modified_by = SubFactory(UserFactory)

    @PostGeneration
    def experimental_ids(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for experimental_id in extracted:
                self.experimental_ids.add(experimental_id)  # type:ignore
        else:
            # Create 1-3 experimental IDs by default
            for _ in range(choice([1, 2, 3])):
                self.experimental_ids.add(ExperimentalIDFactory())  # type:ignore
