from django.contrib.auth import get_user_model
from factory import Faker, PostGenerationMethodCall
from factory.django import DjangoModelFactory

User = get_user_model()


class UserFactory(DjangoModelFactory):
    class Meta:  # type:ignore
        model = User

    email = Faker("email")
    password = PostGenerationMethodCall("set_password", "testing_password")
    is_staff = False
