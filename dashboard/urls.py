from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.home_view, name="home"),
    path("reports/occupancy/", views.occupancy_report_view, name="occupancy_report"),
]