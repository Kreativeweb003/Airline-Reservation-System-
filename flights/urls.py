from django.urls import path
from . import views

app_name = "flights"

urlpatterns = [
    path("routes/", views.route_list_view, name="route_list"),
    path("routes/create/", views.route_create_view, name="route_create"),

    path("", views.flight_list_view, name="list"),
    path("create/", views.flight_create_view, name="create"),
    path("<int:pk>/", views.flight_detail_view, name="detail"),
    path("<int:pk>/pricing/", views.flight_pricing_view, name="pricing"),
    path("<int:pk>/status/", views.flight_status_update_view, name="status_update"),

    path("search/", views.flight_search_view, name="search"),
]