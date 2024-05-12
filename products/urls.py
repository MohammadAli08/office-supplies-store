# Django
from django.urls import path

# Project
from .views import ProductListView, ProductListFilterAjaxView

app_name = "products"


urlpatterns = [
    path("", ProductListView.as_view(), name="list"),
    path("filter-ajax/", ProductListFilterAjaxView.as_view(), name="filter_ajax"),
]

