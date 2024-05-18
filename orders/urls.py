# Django
from django.urls import path

# Project
from . import views
from .views import CartDetailView

app_name = "orders"

urlpatterns = [
    path("", CartDetailView.as_view(), name="cart"),
    path("add-to-order-ajax/", views.add_to_order_ajax, name="add_to_order_ajax"),
    path("remove-from-order-ajax/", views.remove_from_order_ajax, name="remove_from_order_ajax"),
]
