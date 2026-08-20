from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser


class PassengerRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    phone_number = forms.CharField(required=False)

    class Meta:
        model = CustomUser
        fields = [
            "username", "first_name", "last_name",
            "email", "phone_number", "password1", "password2",
        ]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = CustomUser.Role.PASSENGER
        user.email = self.cleaned_data["email"]
        user.phone_number = self.cleaned_data.get("phone_number", "")
        if commit:
            user.save()
        return user


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            "first_name", "last_name", "email",
            "phone_number", "date_of_birth", "passport_number",
        ]
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
        }