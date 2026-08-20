from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone

from flights.models import Seat, FlightSchedule
from .models import Reservation


class SeatUnavailableError(Exception):
    pass


@transaction.atomic
def create_reservation(*, passenger, seat_id, passenger_full_name=None, passenger_passport_number=""):
    try:
        seat = Seat.objects.select_for_update().select_related("flight").get(pk=seat_id)
    except Seat.DoesNotExist:
        raise ValidationError("Seat does not exist.")

    if seat.flight.status != FlightSchedule.Status.SCHEDULED:
        raise ValidationError("This flight is not currently open for booking.")

    if seat.flight.departure_datetime <= timezone.now():
        raise ValidationError("Cannot book a seat on a flight that has already departed.")

    if not seat.is_available:
        raise SeatUnavailableError(f"Seat {seat.seat_number} is no longer available.")

    seat.status = Seat.Status.RESERVED
    seat.save(update_fields=["status"])

    reservation = Reservation.objects.create(
        passenger=passenger,
        flight=seat.flight,
        seat=seat,
        price_paid=seat.price,
        passenger_full_name=passenger_full_name or passenger.get_full_name() or passenger.username,
        passenger_passport_number=passenger_passport_number or getattr(passenger, "passport_number", ""),
    )
    return reservation


@transaction.atomic
def cancel_reservation(*, reservation: Reservation, cancelled_by):
    if reservation.status != Reservation.Status.CONFIRMED:
        raise ValidationError("Only confirmed reservations can be cancelled.")

    is_owner = cancelled_by.id == reservation.passenger_id
    is_admin = getattr(cancelled_by, "is_staff", False) or getattr(cancelled_by, "is_admin_role", False)
    if not (is_owner or is_admin):
        raise ValidationError("You are not authorized to cancel this reservation.")

    if reservation.flight.departure_datetime <= timezone.now():
        raise ValidationError("Cannot cancel a reservation after the flight has departed.")

    seat = Seat.objects.select_for_update().get(pk=reservation.seat_id)
    seat.status = Seat.Status.AVAILABLE
    seat.save(update_fields=["status"])

    reservation.status = Reservation.Status.CANCELLED
    reservation.cancelled_at = timezone.now()
    reservation.save(update_fields=["status", "cancelled_at"])

    return reservation


def get_passenger_reservations(passenger, *, upcoming_only=False):
    qs = Reservation.objects.filter(passenger=passenger).select_related(
        "flight__route__origin", "flight__route__destination", "seat"
    )
    if upcoming_only:
        qs = qs.filter(status=Reservation.Status.CONFIRMED, flight__departure_datetime__gt=timezone.now())
    return qs.order_by("-booked_at")


def get_booking_by_reference(booking_reference: str):
    try:
        return Reservation.objects.select_related(
            "flight__route__origin", "flight__route__destination", "seat", "passenger"
        ).get(booking_reference=booking_reference.upper())
    except Reservation.DoesNotExist:
        return None




