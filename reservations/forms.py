from django import forms


class SeatSelectionForm(forms.Form):
    seat_id = forms.IntegerField(widget=forms.HiddenInput)


class PassengerDetailsForm(forms.Form):
    """Collected at booking time in case the traveler isn't the account holder (e.g. booking for family)."""
    full_name = forms.CharField(max_length=150)
    passport_number = forms.CharField(max_length=30, required=False)