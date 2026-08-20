from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

from aircraft.decorators import admin_required
from .models import Airport
from .forms import AirportForm
from .services import create_airport, deactivate_airport, search_airports


@login_required
@admin_required
def airport_list_view(request):
    query = request.GET.get("q", "")
    airports = search_airports(query) if query else Airport.objects.all()
    return render(request, "airports/airport_list.html", {
        "airports": airports, "query": query,
    })


@login_required
@admin_required
def airport_create_view(request):
    if request.method == "POST":
        form = AirportForm(request.POST)
        if form.is_valid():
            try:
                create_airport(**form.cleaned_data)
                messages.success(request, "Airport created.")
                return redirect("airports:list")
            except ValidationError as e:
                form.add_error("iata_code", str(e))
    else:
        form = AirportForm()
    return render(request, "airports/airport_form.html", {"form": form, "mode": "create"})


@login_required
@admin_required
def airport_update_view(request, pk):
    airport = get_object_or_404(Airport, pk=pk)
    if request.method == "POST":
        form = AirportForm(request.POST, instance=airport)
        if form.is_valid():
            form.save()
            messages.success(request, "Airport updated.")
            return redirect("airports:list")
    else:
        form = AirportForm(instance=airport)
    return render(request, "airports/airport_form.html", {"form": form, "mode": "edit", "airport": airport})


@login_required
@admin_required
def airport_deactivate_view(request, pk):
    airport = get_object_or_404(Airport, pk=pk)
    if request.method == "POST":
        deactivate_airport(airport)
        messages.info(request, f"{airport.iata_code} deactivated.")
    return redirect("airports:list")


def airport_autocomplete_view(request):
    """Used by flight search (accessible to passengers too) — no admin check."""
    query = request.GET.get("q", "")
    airports = search_airports(query)[:10]
    results = [
        {"id": a.id, "label": f"{a.iata_code} — {a.city}, {a.country}"}
        for a in airports
    ]
    return JsonResponse({"results": results})



