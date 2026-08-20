from django import forms
from .models import Airport


class AirportForm(forms.ModelForm):
    class Meta:
        model = Airport
        fields = ["iata_code", "name", "city", "country", "timezone", "is_active"]
        widgets = {
            "iata_code": forms.TextInput(attrs={"maxlength": 3, "style": "text-transform:uppercase"}),
        }

    def clean_iata_code(self):
        code = self.cleaned_data["iata_code"].upper().strip()
        if len(code) != 3 or not code.isalpha():
            raise forms.ValidationError("IATA code must be exactly 3 letters.")
        return code