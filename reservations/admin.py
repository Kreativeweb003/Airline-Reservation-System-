from django.contrib import admin
from .models import Reservation


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ["booking_reference", "passenger", "flight", "seat", "status", "price_paid", "booked_at"]
    list_filter = ["status", "flight"]
    search_fields = ["booking_reference", "passenger__username", "passenger_full_name"]
    readonly_fields = ["booking_reference", "booked_at"]