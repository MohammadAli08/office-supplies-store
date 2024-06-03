# Django
from django.urls import path

# Project
from .views import DashboardView


app_name = "user_panels"

urlpatterns = [
    path("", DashboardView.as_view(), name="dashboard")
]
