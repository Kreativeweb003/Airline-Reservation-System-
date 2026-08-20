from django.contrib import admin
from .models import Aircraft, SeatConfiguration


class SeatConfigurationInline(admin.TabularInline):
    model = SeatConfiguration
    extra = 1


@admin.register(Aircraft)
class AircraftAdmin(admin.ModelAdmin):
    list_display = ["registration_number", "model_name", "manufacturer", "total_capacity", "is_active"]
    list_filter = ["manufacturer", "is_active"]
    search_fields = ["registration_number", "model_name"]
    inlines = [SeatConfigurationInline]