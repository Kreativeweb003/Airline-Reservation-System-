from django.urls import path
from . import views

app_name = "aircraft"

urlpatterns = [
    path("", views.aircraft_list_view, name="list"),
    path("create/", views.aircraft_create_view, name="create"),
    path("<int:pk>/", views.aircraft_detail_view, name="detail"),
    path("<int:pk>/edit/", views.aircraft_update_view, name="edit"),
    path("<int:pk>/deactivate/", views.aircraft_deactivate_view, name="deactivate"),
]