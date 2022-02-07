from factory import Faker
from factory.django import DjangoModelFactory
from django.contrib.auth import get_user_model

User = get_user_model()


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = Faker("email")
    email = Faker("email")
    password = "testing_password"
    is_staff = False
