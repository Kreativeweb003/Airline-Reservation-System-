from django.db import transaction
from django.core.exceptions import ValidationError

from .models import FlightSchedule, FlightClassPrice, Seat


@transaction.atomic
def create_flight_schedule(*, flight_number, route, aircraft, departure_datetime, arrival_datetime, gate=""):
    flight = FlightSchedule(
        flight_number=flight_number,
        route=route,
        aircraft=aircraft,
        departure_datetime=departure_datetime,
        arrival_datetime=arrival_datetime,
        gate=gate,
        status=FlightSchedule.Status.DRAFT,
    )
    flight.full_clean()
    flight.save()
    return flight


@transaction.atomic
def set_pricing_and_generate_seats(*, flight: FlightSchedule, price_map: dict):
    """
    price_map: {"ECONOMY": 50000, "BUSINESS": 120000, ...}
    Must cover every seat class configured on the flight's aircraft.
    Generates one Seat row per physical seat on the aircraft, priced by class.
    Safe to call only once per flight (DRAFT -> SCHEDULED).
    """
    if flight.status != FlightSchedule.Status.DRAFT:
        raise ValidationError("Seats have already been generated for this flight.")

    configs = list(flight.aircraft.seat_configurations.all())
    if not configs:
        raise ValidationError("Aircraft has no seat configuration defined.")

    missing = [c.seat_class for c in configs if c.seat_class not in price_map]
    if missing:
        raise ValidationError(f"Missing price for seat class(es): {', '.join(missing)}")

    # Persist pricing
    for cfg in configs:
        FlightClassPrice.objects.update_or_create(
            flight=flight,
            seat_class=cfg.seat_class,
            defaults={"price": price_map[cfg.seat_class]},
        )

    # Generate seats
    seats_to_create = []
    for cfg in configs:
        for row, col, seat_class in cfg.generate_seat_labels():
            seats_to_create.append(Seat(
                flight=flight,
                seat_number=f"{row}{col}",
                row=row,
                column=col,
                seat_class=seat_class,
                price=price_map[seat_class],
            ))

    Seat.objects.bulk_create(seats_to_create)

    flight.status = FlightSchedule.Status.SCHEDULED
    flight.save(update_fields=["status"])

    return flight


def search_flights(*, origin_id=None, destination_id=None, travel_date=None):
    qs = FlightSchedule.objects.filter(status=FlightSchedule.Status.SCHEDULED).select_related(
        "route__origin", "route__destination", "aircraft"
    )
    if origin_id:
        qs = qs.filter(route__origin_id=origin_id)
    if destination_id:
        qs = qs.filter(route__destination_id=destination_id)
    if travel_date:
        qs = qs.filter(departure_datetime__date=travel_date)
    return qs.order_by("departure_datetime")


def update_flight_status(flight: FlightSchedule, new_status: str):
    if new_status not in FlightSchedule.Status.values:
        raise ValidationError("Invalid status.")
    if flight.status == FlightSchedule.Status.DRAFT and new_status != FlightSchedule.Status.CANCELLED:
        raise ValidationError("Cannot change status of a DRAFT flight until pricing is set.")
    flight.status = new_status
    flight.save(update_fields=["status"])


def list_available_flights():
    """All bookable flights, soonest first — used for browse-style listing (vs. filtered search)."""
    return FlightSchedule.objects.filter(
        status=FlightSchedule.Status.SCHEDULED,
        departure_datetime__gt=timezone.now(),
    ).select_related(
        "route__origin", "route__destination", "aircraft"
    ).order_by("departure_datetime")







