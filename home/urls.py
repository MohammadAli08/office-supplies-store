# Django
from django.urls import path

# Project
from . import views


app_name = "home"

urlpatterns = [
    path("", views.index, name="index"),
]
