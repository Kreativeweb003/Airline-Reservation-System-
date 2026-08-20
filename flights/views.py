from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect, get_object_or_404

from aircraft.decorators import admin_required
from .models import Route, FlightSchedule
from .forms import RouteForm, FlightScheduleForm, FlightPricingForm, FlightSearchForm
from .services import (
    create_flight_schedule, set_pricing_and_generate_seats,
    search_flights, update_flight_status,
)


# ---- Routes (admin) ----

@admin_required
def route_list_view(request):
    routes = Route.objects.select_related("origin", "destination").all()
    return render(request, "flights/route_list.html", {"routes": routes})


@admin_required
def route_create_view(request):
    if request.method == "POST":
        form = RouteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Route created.")
            return redirect("flights:route_list")
    else:
        form = RouteForm()
    return render(request, "flights/route_form.html", {"form": form})


# ---- Flight schedules (admin) ----

@admin_required
def flight_list_view(request):
    flights = FlightSchedule.objects.select_related("route__origin", "route__destination", "aircraft").all()
    return render(request, "flights/flight_list.html", {"flights": flights})


@admin_required
def flight_detail_view(request, pk):
    flight = get_object_or_404(FlightSchedule, pk=pk)
    return render(request, "flights/flight_detail.html", {"flight": flight})


@admin_required
def flight_create_view(request):
    if request.method == "POST":
        form = FlightScheduleForm(request.POST)
        if form.is_valid():
            try:
                flight = create_flight_schedule(
                    flight_number=form.cleaned_data["flight_number"],
                    route=form.cleaned_data["route"],
                    aircraft=form.cleaned_data["aircraft"],
                    departure_datetime=form.cleaned_data["departure_datetime"],
                    arrival_datetime=form.cleaned_data["arrival_datetime"],
                    gate=form.cleaned_data.get("gate", ""),
                )
                messages.success(request, "Flight created as draft. Set pricing to activate it.")
                return redirect("flights:pricing", pk=flight.pk)
            except ValidationError as e:
                form.add_error(None, str(e))
    else:
        form = FlightScheduleForm()
    return render(request, "flights/flight_form.html", {"form": form})


@admin_required
def flight_pricing_view(request, pk):
    flight = get_object_or_404(FlightSchedule, pk=pk)
    seat_classes = list(
        flight.aircraft.seat_configurations.values_list("seat_class", flat=True)
    )

    if flight.status != FlightSchedule.Status.DRAFT:
        messages.info(request, "Pricing has already been set for this flight.")
        return redirect("flights:detail", pk=flight.pk)

    if request.method == "POST":
        form = FlightPricingForm(request.POST, seat_classes=seat_classes)
        if form.is_valid():
            try:
                set_pricing_and_generate_seats(flight=flight, price_map=form.get_price_map())
                messages.success(request, "Pricing set and seats generated. Flight is now scheduled.")
                return redirect("flights:detail", pk=flight.pk)
            except ValidationError as e:
                form.add_error(None, str(e))
    else:
        form = FlightPricingForm(seat_classes=seat_classes)

    return render(request, "flights/flight_pricing.html", {"form": form, "flight": flight})


@admin_required
def flight_status_update_view(request, pk):
    flight = get_object_or_404(FlightSchedule, pk=pk)
    if request.method == "POST":
        new_status = request.POST.get("status")
        try:
            update_flight_status(flight, new_status)
            messages.success(request, f"Flight status updated to {new_status}.")
        except ValidationError as e:
            messages.error(request, str(e))
    return redirect("flights:detail", pk=flight.pk)


# ---- Passenger-facing search ----

def flight_search_view(request):
    form = FlightSearchForm(request.GET or None)
    results = []
    if form.is_valid():
        results = search_flights(
            origin_id=form.cleaned_data["origin"].id,
            destination_id=form.cleaned_data["destination"].id,
            travel_date=form.cleaned_data["travel_date"],
        )
    return render(request, "flights/flight_search.html", {"form": form, "results": results})


