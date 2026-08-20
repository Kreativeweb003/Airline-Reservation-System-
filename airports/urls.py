from django.urls import path
from . import views

app_name = "airports"

urlpatterns = [
    path("", views.airport_list_view, name="list"),
    path("create/", views.airport_create_view, name="create"),
    path("<int:pk>/edit/", views.airport_update_view, name="edit"),
    path("<int:pk>/deactivate/", views.airport_deactivate_view, name="deactivate"),
    path("autocomplete/", views.airport_autocomplete_view, name="autocomplete"),
]
