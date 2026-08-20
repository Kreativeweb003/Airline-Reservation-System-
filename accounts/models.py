from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models


class CustomUserManager(UserManager):
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("role", CustomUser.Role.ADMIN)
        return super().create_superuser(username, email, password, **extra_fields)


class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        PASSENGER = "PASSENGER", "Passenger"
        ADMIN = "ADMIN", "Administrator"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.PASSENGER,
    )
    phone_number = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    passport_number = models.CharField(max_length=30, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.role})"

    @property
    def is_passenger(self):
        return self.role == self.Role.PASSENGER

    @property
    def is_admin_role(self):
        return self.role == self.Role.ADMIN



