# Django
from django.urls import path

# Project
from .views import (
    ProductListView, ProductListFilterAjaxView,
    ProductDetailView, get_comments,
    like_or_dislike_ajax
)

app_name = "products"


urlpatterns = [
    # list
    path("", ProductListView.as_view(), name="list"),
    path("filter-ajax/", ProductListFilterAjaxView.as_view(), name="filter_ajax"),
    # detail
    path("<int:product_id>/", ProductDetailView.as_view(), name="detail"),
    path("<int:product_id>/get-comments-ajax/<int:page>/",
         get_comments, name="get_comments_ajax"),
    path("<int:product_id>/like-or-dislike-ajax/",
         like_or_dislike_ajax, name="like_or_dislike_ajax")
]
