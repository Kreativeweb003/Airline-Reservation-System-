from django.contrib import admin
from .models import Airport


@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    list_display = ["iata_code", "name", "city", "country", "is_active"]
    list_filter = ["is_active", "country"]
    search_fields = ["iata_code", "name", "city", "country"]
    ordering = ["city"]