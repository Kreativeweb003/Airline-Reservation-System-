from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404

from aircraft.decorators import admin_required
from .models import Aircraft
from .forms import AircraftForm, SeatConfigurationFormSet
from .services import validate_no_row_overlap, deactivate_aircraft


@admin_required
def aircraft_list_view(request):
    aircraft = Aircraft.objects.all()
    return render(request, "aircraft/aircraft_list.html", {"aircraft": aircraft})


@admin_required
def aircraft_detail_view(request, pk):
    aircraft = get_object_or_404(Aircraft, pk=pk)
    return render(request, "aircraft/aircraft_detail.html", {"aircraft": aircraft})


@admin_required
def aircraft_create_view(request):
    if request.method == "POST":
        form = AircraftForm(request.POST)
        formset = SeatConfigurationFormSet(request.POST, instance=Aircraft())
        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    aircraft = form.save()
                    formset.instance = aircraft
                    configs = formset.save(commit=False)
                    validate_no_row_overlap(aircraft, configs)
                    for cfg in configs:
                        cfg.aircraft = aircraft
                        cfg.full_clean()
                        cfg.save()
                messages.success(request, "Aircraft created with seat configuration.")
                return redirect("aircraft:detail", pk=aircraft.pk)
            except ValidationError as e:
                messages.error(request, str(e))
    else:
        form = AircraftForm()
        formset = SeatConfigurationFormSet(instance=Aircraft())

    return render(request, "aircraft/aircraft_form.html", {
        "form": form, "formset": formset, "mode": "create",
    })


@admin_required
def aircraft_update_view(request, pk):
    aircraft = get_object_or_404(Aircraft, pk=pk)
    if request.method == "POST":
        form = AircraftForm(request.POST, instance=aircraft)
        formset = SeatConfigurationFormSet(request.POST, instance=aircraft)
        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    form.save()
                    configs = formset.save(commit=False)
                    validate_no_row_overlap(aircraft, list(aircraft.seat_configurations.all()) + configs)
                    for cfg in configs:
                        cfg.aircraft = aircraft
                        cfg.full_clean()
                        cfg.save()
                    for obj in formset.deleted_objects:
                        obj.delete()
                messages.success(request, "Aircraft updated.")
                return redirect("aircraft:detail", pk=aircraft.pk)
            except ValidationError as e:
                messages.error(request, str(e))
    else:
        form = AircraftForm(instance=aircraft)
        formset = SeatConfigurationFormSet(instance=aircraft)

    return render(request, "aircraft/aircraft_form.html", {
        "form": form, "formset": formset, "mode": "edit", "aircraft": aircraft,
    })


@admin_required
def aircraft_deactivate_view(request, pk):
    aircraft = get_object_or_404(Aircraft, pk=pk)
    if request.method == "POST":
        deactivate_aircraft(aircraft)
        messages.info(request, f"{aircraft.registration_number} deactivated.")
    return redirect("aircraft:list")