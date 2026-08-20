from django.db import models
from django.core.exceptions import ValidationError

from airports.models import Airport
from aircraft.models import Aircraft, SeatConfiguration


class Route(models.Model):
    origin = models.ForeignKey(Airport, on_delete=models.PROTECT, related_name="departing_routes")
    destination = models.ForeignKey(Airport, on_delete=models.PROTECT, related_name="arriving_routes")
    distance_km = models.PositiveIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["origin", "destination"], name="unique_route"),
        ]

    def __str__(self):
        return f"{self.origin.iata_code} → {self.destination.iata_code}"

    def clean(self):
        if self.origin_id and self.destination_id and self.origin_id == self.destination_id:
            raise ValidationError("Origin and destination cannot be the same airport.")


class FlightSchedule(models.Model):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft (pricing pending)"
        SCHEDULED = "SCHEDULED", "Scheduled"
        DELAYED = "DELAYED", "Delayed"
        CANCELLED = "CANCELLED", "Cancelled"
        DEPARTED = "DEPARTED", "Departed"
        ARRIVED = "ARRIVED", "Arrived"

    flight_number = models.CharField(max_length=10)
    route = models.ForeignKey(Route, on_delete=models.PROTECT, related_name="flights")
    aircraft = models.ForeignKey(Aircraft, on_delete=models.PROTECT, related_name="flights")
    departure_datetime = models.DateTimeField()
    arrival_datetime = models.DateTimeField()
    gate = models.CharField(max_length=10, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["departure_datetime"]
        constraints = [
            models.UniqueConstraint(
                fields=["flight_number", "departure_datetime"], name="unique_flight_instance"
            ),
        ]

    def __str__(self):
        return f"{self.flight_number} — {self.route} @ {self.departure_datetime:%Y-%m-%d %H:%M}"

    def clean(self):
        if self.departure_datetime and self.arrival_datetime:
            if self.arrival_datetime <= self.departure_datetime:
                raise ValidationError("Arrival must be after departure.")

    @property
    def duration(self):
        return self.arrival_datetime - self.departure_datetime

    @property
    def total_seats(self):
        return self.seats.count()

    @property
    def available_seats_count(self):
        return self.seats.filter(status=Seat.Status.AVAILABLE).count()

    @property
    def occupancy_rate(self):
        total = self.total_seats
        if total == 0:
            return 0
        booked = total - self.available_seats_count
        return round((booked / total) * 100, 1)

    @property
    def is_bookable(self):
        return self.status == self.Status.SCHEDULED and self.available_seats_count > 0


class FlightClassPrice(models.Model):
    flight = models.ForeignKey(FlightSchedule, on_delete=models.CASCADE, related_name="class_prices")
    seat_class = models.CharField(max_length=20, choices=SeatConfiguration.SeatClass.choices)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["flight", "seat_class"], name="unique_price_per_class"),
        ]

    def __str__(self):
        return f"{self.flight.flight_number} — {self.seat_class}: {self.price}"


class Seat(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = "AVAILABLE", "Available"
        RESERVED = "RESERVED", "Reserved"
        BLOCKED = "BLOCKED", "Blocked"

    flight = models.ForeignKey(FlightSchedule, on_delete=models.CASCADE, related_name="seats")
    seat_number = models.CharField(max_length=6)   # e.g. "12A"
    row = models.PositiveIntegerField()
    column = models.CharField(max_length=1)
    seat_class = models.CharField(max_length=20, choices=SeatConfiguration.SeatClass.choices)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.AVAILABLE)

    class Meta:
        ordering = ["row", "column"]
        constraints = [
            models.UniqueConstraint(fields=["flight", "seat_number"], name="unique_seat_per_flight"),
        ]

    def __str__(self):
        return f"{self.flight.flight_number} — Seat {self.seat_number} ({self.seat_class})"

    @property
    def is_available(self):
        return self.status == self.Status.AVAILABLE





