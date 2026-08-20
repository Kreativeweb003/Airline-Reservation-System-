from django.utils import timezone
from django.db.models import Count, Q, Avg

from flights.models import FlightSchedule, Seat
from reservations.models import Reservation
from accounts.models import CustomUser


def get_admin_stats():
    now = timezone.now()

    total_flights = FlightSchedule.objects.count()
    upcoming_flights = FlightSchedule.objects.filter(
        departure_datetime__gt=now,
        status=FlightSchedule.Status.SCHEDULED,
    ).count()

    total_reservations = Reservation.objects.count()
    confirmed_reservations = Reservation.objects.filter(status=Reservation.Status.CONFIRMED).count()
    cancelled_reservations = Reservation.objects.filter(status=Reservation.Status.CANCELLED).count()

    total_passengers = CustomUser.objects.filter(role=CustomUser.Role.PASSENGER).count()

    total_seats = Seat.objects.count()
    reserved_seats = Seat.objects.filter(status=Seat.Status.RESERVED).count()
    overall_occupancy_rate = round((reserved_seats / total_seats) * 100, 1) if total_seats else 0

    return {
        "total_flights": total_flights,
        "upcoming_flights": upcoming_flights,
        "total_reservations": total_reservations,
        "confirmed_reservations": confirmed_reservations,
        "cancelled_reservations": cancelled_reservations,
        "total_passengers": total_passengers,
        "overall_occupancy_rate": overall_occupancy_rate,
    }


def get_flight_occupancy_report(*, status=None, limit=20):
    """Per-flight breakdown, used for the admin reporting page."""
    qs = FlightSchedule.objects.select_related(
        "route__origin", "route__destination", "aircraft"
    ).annotate(
        seat_count=Count("seats"),
        reserved_count=Count("seats", filter=Q(seats__status=Seat.Status.RESERVED)),
    )
    if status:
        qs = qs.filter(status=status)

    flights = qs.order_by("-departure_datetime")[:limit]

    report = []
    for f in flights:
        occupancy = round((f.reserved_count / f.seat_count) * 100, 1) if f.seat_count else 0
        report.append({
            "flight": f,
            "seat_count": f.seat_count,
            "reserved_count": f.reserved_count,
            "occupancy_rate": occupancy,
        })
    return report


def get_recent_reservations(limit=10):
    return Reservation.objects.select_related(
        "passenger", "flight__route__origin", "flight__route__destination"
    ).order_by("-booked_at")[:limit]


def get_upcoming_departures(limit=10):
    now = timezone.now()
    return FlightSchedule.objects.filter(
        departure_datetime__gt=now,
        status=FlightSchedule.Status.SCHEDULED,
    ).select_related("route__origin", "route__destination").order_by("departure_datetime")[:limit]



