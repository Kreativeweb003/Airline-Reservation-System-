from django.db import transaction
from .models import CustomUser


class RegistrationError(Exception):
    pass


@transaction.atomic
def register_passenger(*, username, email, password, first_name, last_name, phone_number=""):
    if CustomUser.objects.filter(username=username).exists():
        raise RegistrationError("Username already taken.")
    if CustomUser.objects.filter(email=email).exists():
        raise RegistrationError("An account with this email already exists.")

    user = CustomUser.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
        phone_number=phone_number,
        role=CustomUser.Role.PASSENGER,
    )
    return user


def create_staff_user(*, username, email, password, first_name, last_name):
    """Used by superuser/admin dashboard to onboard airline staff."""
    user = CustomUser.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
        role=CustomUser.Role.ADMIN,
        is_staff=True,
    )
    return user