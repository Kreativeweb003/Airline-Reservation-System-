from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from aircraft.decorators import admin_required
from reservations.services import get_passenger_reservations
from .services import (
    get_admin_stats, get_flight_occupancy_report,
    get_recent_reservations, get_upcoming_departures,
)


@login_required
def home_view(request):
    """Routes to the right dashboard based on role."""
    if request.user.is_staff or request.user.is_admin_role:
        return admin_dashboard_view(request)
    return passenger_dashboard_view(request)


def passenger_dashboard_view(request):
    upcoming = get_passenger_reservations(request.user, upcoming_only=True)[:5]
    recent = get_passenger_reservations(request.user)[:5]
    return render(request, "dashboard/passenger_home.html", {
        "upcoming": upcoming,
        "recent": recent,
    })


@admin_required
def admin_dashboard_view(request):
    stats = get_admin_stats()
    recent_reservations = get_recent_reservations()
    upcoming_departures = get_upcoming_departures()
    return render(request, "dashboard/admin_home.html", {
        "stats": stats,
        "recent_reservations": recent_reservations,
        "upcoming_departures": upcoming_departures,
    })


@admin_required
def occupancy_report_view(request):
    status_filter = request.GET.get("status", "")
    report = get_flight_occupancy_report(status=status_filter or None)
    return render(request, "dashboard/occupancy_report.html", {
        "report": report,
        "status_filter": status_filter,
    })



