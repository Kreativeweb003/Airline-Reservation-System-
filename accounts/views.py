from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.shortcuts import render, redirect

from .forms import PassengerRegistrationForm, ProfileUpdateForm
from .services import register_passenger, RegistrationError


def register_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard:home")

    if request.method == "POST":
        form = PassengerRegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = register_passenger(
                    username=form.cleaned_data["username"],
                    email=form.cleaned_data["email"],
                    password=form.cleaned_data["password1"],
                    first_name=form.cleaned_data["first_name"],
                    last_name=form.cleaned_data["last_name"],
                    phone_number=form.cleaned_data.get("phone_number", ""),
                )
                login(request, user)
                messages.success(request, "Account created successfully.")
                return redirect("dashboard:home")
            except RegistrationError as e:
                form.add_error(None, str(e))
    else:
        form = PassengerRegistrationForm()

    return render(request, "accounts/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard:home")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"],
            )
            if user is not None:
                login(request, user)
                return redirect("dashboard:home")
        messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, "accounts/login.html", {"form": form})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("accounts:login")


@login_required
def profile_view(request):
    return render(request, "accounts/profile.html", {"user_obj": request.user})


@login_required
def profile_update_view(request):
    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect("accounts:profile")
    else:
        form = ProfileUpdateForm(instance=request.user)

    return render(request, "accounts/profile_edit.html", {"form": form})








