from django.contrib import admin
from .models import Route, FlightSchedule, FlightClassPrice, Seat


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ["origin", "destination", "distance_km", "is_active"]
    list_filter = ["is_active"]


class FlightClassPriceInline(admin.TabularInline):
    model = FlightClassPrice
    extra = 0


@admin.register(FlightSchedule)
class FlightScheduleAdmin(admin.ModelAdmin):
    list_display = ["flight_number", "route", "aircraft", "departure_datetime", "status", "occupancy_rate"]
    list_filter = ["status", "route"]
    search_fields = ["flight_number"]
    inlines = [FlightClassPriceInline]


@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ["flight", "seat_number", "seat_class", "price", "status"]
    list_filter = ["seat_class", "status", "flight"]
    search_fields = ["seat_number"]