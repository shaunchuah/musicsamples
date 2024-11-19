import string

from users.utils import generate_random_password


def test_generate_random_password_length():
    length = 20
    password = generate_random_password(length)
    assert len(password) == length


def test_generate_random_password_characters():
    password = generate_random_password()
    allowed_characters = string.ascii_letters + string.digits
    for char in password:
        assert char in allowed_characters


def test_generate_random_password_uniqueness():
    passwords = {generate_random_password() for _ in range(1000)}
    assert len(passwords) == 1000
