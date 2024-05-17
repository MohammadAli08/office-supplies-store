from django.contrib import admin

from .models import Order, OrderItem


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["user", "first_name", "last_name", "is_paid"]
    list_editable = ["is_paid"]
    list_filter = ["is_paid"]
    search_fields = ["user", "first_name", "last_name", "address", "phone"]
    raw_id_fields = ["user"]
    date_hierarchy = "payment_date"


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ["order", "product", "quantity", "paid_price", "discount"]
    list_editable = ["quantity", "paid_price", "discount"]
    list_filter = ["order", "product"]
    search_fields = ["order", "product"]
    raw_id_fields = ["order", "product"]
