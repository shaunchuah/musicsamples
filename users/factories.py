from django.contrib.auth import get_user_model
from factory import Faker
from factory.django import DjangoModelFactory

User = get_user_model()


class UserFactory(DjangoModelFactory):
    class Meta:  # type:ignore
        model = User

    email = Faker("email")
    password = "testing_password"
    is_staff = False
