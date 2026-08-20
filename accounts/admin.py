from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ["username", "email", "first_name", "last_name", "role", "is_staff"]
    list_filter = ["role", "is_staff", "is_active"]
    fieldsets = UserAdmin.fieldsets + (
        ("Airline Profile", {
            "fields": ("role", "phone_number", "date_of_birth", "passport_number"),
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Airline Profile", {
            "fields": ("role", "phone_number"),
        }),
    )