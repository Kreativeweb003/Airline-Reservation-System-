from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect, get_object_or_404

from flights.models import FlightSchedule, Seat
from .forms import PassengerDetailsForm
from .models import Reservation
from .services import (
    create_reservation, cancel_reservation, SeatUnavailableError,
    get_passenger_reservations, get_booking_by_reference,
)


@login_required
def seat_map_view(request, flight_id):
    flight = get_object_or_404(FlightSchedule, pk=flight_id)
    if not flight.is_bookable:
        messages.error(request, "This flight is not available for booking.")
        return redirect("flights:search")

    seats = flight.seats.all().order_by("row", "column")
    return render(request, "reservations/seat_map.html", {"flight": flight, "seats": seats})


@login_required
def book_seat_view(request, flight_id, seat_id):
    flight = get_object_or_404(FlightSchedule, pk=flight_id)
    seat = get_object_or_404(Seat, pk=seat_id, flight=flight)

    if request.method == "POST":
        form = PassengerDetailsForm(request.POST)
        if form.is_valid():
            try:
                reservation = create_reservation(
                    passenger=request.user,
                    seat_id=seat.id,
                    passenger_full_name=form.cleaned_data["full_name"],
                    passenger_passport_number=form.cleaned_data.get("passport_number", ""),
                )
                messages.success(request, f"Booking confirmed! Reference: {reservation.booking_reference}")
                return redirect("reservations:detail", pk=reservation.pk)
            except SeatUnavailableError as e:
                messages.error(request, str(e))
                return redirect("reservations:seat_map", flight_id=flight.id)
            except ValidationError as e:
                messages.error(request, str(e))
    else:
        initial = {
            "full_name": request.user.get_full_name() or request.user.username,
            "passport_number": getattr(request.user, "passport_number", ""),
        }
        form = PassengerDetailsForm(initial=initial)

    return render(request, "reservations/booking_confirm.html", {
        "flight": flight, "seat": seat, "form": form,
    })


@login_required
def reservation_detail_view(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk)
    is_owner = reservation.passenger_id == request.user.id
    is_admin = request.user.is_staff or getattr(request.user, "is_admin_role", False)
    if not (is_owner or is_admin):
        messages.error(request, "You do not have permission to view this booking.")
        return redirect("dashboard:home")
    return render(request, "reservations/reservation_detail.html", {"reservation": reservation})


@login_required
def my_reservations_view(request):
    upcoming = get_passenger_reservations(request.user, upcoming_only=True)
    all_bookings = get_passenger_reservations(request.user)
    return render(request, "reservations/my_reservations.html", {
        "upcoming": upcoming, "all_bookings": all_bookings,
    })


@login_required
def cancel_reservation_view(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk)
    if request.method == "POST":
        try:
            cancel_reservation(reservation=reservation, cancelled_by=request.user)
            messages.success(request, "Reservation cancelled.")
        except ValidationError as e:
            messages.error(request, str(e))
    return redirect("reservations:my_reservations")


def lookup_booking_view(request):
    """Public lookup by reference, e.g. for guest 'manage my booking' flow."""
    reservation = None
    reference = request.GET.get("reference", "")
    if reference:
        reservation = get_booking_by_reference(reference)
        if not reservation:
            messages.error(request, "No booking found with that reference.")
    return render(request, "reservations/lookup_booking.html", {"reservation": reservation, "reference": reference})




