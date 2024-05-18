import json
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.http import HttpRequest

from orders.models import Order, OrderItem
from products.models import Product, ProductColorVariant

from .models import User


@receiver(user_logged_in)
def save_cookies_data(sender, user: User, request:HttpRequest, **kwargs):
    cookies = request.COOKIES
    if order := cookies.get("order"):
        user_order, _ = Order.in_processes.get_or_create(user=user)
        user_items = user_order.items
        if user.is_superuser:
            all_products = ProductColorVariant.objects.all()
        else:
            all_products = ProductColorVariant.objects.filter(
                product__is_active=True)

        try:
            order = list(json.loads(order))
        except:
            pass

        for item in order:
            try:
                product = all_products.get(id=item["product"])
            except:
                continue

            if not user_items.filter(product=product).exists():
                order_item = OrderItem(
                    order=user_order, product=product, quantity=item.get("quantity"))
                try:
                    order_item.clean_fields()
                except:
                    continue
                order_item.save()
    if liked_products := cookies.get("liked_products"):
        try:
            liked_products = list(json.loads(liked_products))
        except:
            return 

        all_products = Product.access_controlled.access_level(user)
        for liked_product in liked_products:
            try:
                product = all_products.get(id=liked_product)
            except:
                continue
            user.liked_products.add(product)
