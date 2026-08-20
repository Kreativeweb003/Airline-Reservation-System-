from django import forms
from django.forms import inlineformset_factory
from .models import Aircraft, SeatConfiguration


class AircraftForm(forms.ModelForm):
    class Meta:
        model = Aircraft
        fields = ["model_name", "manufacturer", "registration_number", "is_active"]


class SeatConfigurationForm(forms.ModelForm):
    class Meta:
        model = SeatConfiguration
        fields = ["seat_class", "row_start", "row_end", "columns"]
        widgets = {
            "columns": forms.TextInput(attrs={"placeholder": "e.g. ABCDEF"}),
        }


SeatConfigurationFormSet = inlineformset_factory(
    Aircraft,
    SeatConfiguration,
    form=SeatConfigurationForm,
    extra=1,
    can_delete=True,
)