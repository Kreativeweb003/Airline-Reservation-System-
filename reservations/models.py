import uuid
from django.db import models
from django.conf import settings

from flights.models import FlightSchedule, Seat


class Reservation(models.Model):
    class Status(models.TextChoices):
        CONFIRMED = "CONFIRMED", "Confirmed"
        CANCELLED = "CANCELLED", "Cancelled"
        COMPLETED = "COMPLETED", "Completed"   # after flight has arrived

    booking_reference = models.CharField(max_length=10, unique=True, editable=False)
    passenger = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="reservations")
    flight = models.ForeignKey(FlightSchedule, on_delete=models.PROTECT, related_name="reservations")
    seat = models.OneToOneField(Seat, on_delete=models.PROTECT, related_name="reservation")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.CONFIRMED)
    price_paid = models.DecimalField(max_digits=10, decimal_places=2)
    passenger_full_name = models.CharField(max_length=150)
    passenger_passport_number = models.CharField(max_length=30, blank=True)
    booked_at = models.DateTimeField(auto_now_add=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-booked_at"]

    def __str__(self):
        return f"{self.booking_reference} — {self.passenger} — {self.flight.flight_number}"

    def save(self, *args, **kwargs):
        if not self.booking_reference:
            self.booking_reference = self._generate_reference()
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_reference():
        # 8-char alphanumeric, e.g. "A1B2C3D4"
        return uuid.uuid4().hex[:8].upper()

    @property
    def is_upcoming(self):
        from django.utils import timezone
        return self.status == self.Status.CONFIRMED and self.flight.departure_datetime > timezone.now()

    @property
    def is_cancellable(self):
        from django.utils import timezone
        return self.status == self.Status.CONFIRMED and self.flight.departure_datetime > timezone.now()