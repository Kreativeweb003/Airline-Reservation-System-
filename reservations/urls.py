from django.urls import path
from . import views

app_name = "reservations"

urlpatterns = [
    path("flight/<int:flight_id>/seats/", views.seat_map_view, name="seat_map"),
    path("flight/<int:flight_id>/seats/<int:seat_id>/book/", views.book_seat_view, name="book_seat"),
    path("<int:pk>/", views.reservation_detail_view, name="detail"),
    path("<int:pk>/cancel/", views.cancel_reservation_view, name="cancel"),
    path("my-bookings/", views.my_reservations_view, name="my_reservations"),
    path("lookup/", views.lookup_booking_view, name="lookup"),
]
