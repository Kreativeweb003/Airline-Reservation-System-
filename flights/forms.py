from django import forms
from django.core.exceptions import ValidationError

from .models import Route, FlightSchedule
from airports.models import Airport


class RouteForm(forms.ModelForm):
    class Meta:
        model = Route
        fields = ["origin", "destination", "distance_km", "is_active"]

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("origin") == cleaned.get("destination"):
            raise ValidationError("Origin and destination cannot be the same airport.")
        return cleaned


class FlightScheduleForm(forms.ModelForm):
    class Meta:
        model = FlightSchedule
        fields = ["flight_number", "route", "aircraft", "departure_datetime", "arrival_datetime", "gate"]
        widgets = {
            "departure_datetime": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "arrival_datetime": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }


class FlightPricingForm(forms.Form):
    """Dynamically built in the view: one price field per seat class on the flight's aircraft."""
    def __init__(self, *args, seat_classes=None, **kwargs):
        super().__init__(*args, **kwargs)
        for seat_class in seat_classes or []:
            self.fields[f"price_{seat_class}"] = forms.DecimalField(
                label=f"{seat_class.title()} price",
                min_value=0,
                max_digits=10,
                decimal_places=2,
            )

    def get_price_map(self):
        return {
            key.replace("price_", ""): value
            for key, value in self.cleaned_data.items()
            if key.startswith("price_")
        }


class FlightSearchForm(forms.Form):
    origin = forms.ModelChoiceField(queryset=Airport.objects.filter(is_active=True), required=True)
    destination = forms.ModelChoiceField(queryset=Airport.objects.filter(is_active=True), required=True)
    travel_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}), required=True)

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("origin") == cleaned.get("destination"):
            raise ValidationError("Origin and destination cannot be the same.")
        return cleaned