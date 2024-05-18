# Python
import json

# Django
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import View
from django.views.decorators.http import require_GET
from django.template.loader import render_to_string


# Project
from .models import Order, OrderItem
from products.models import ProductColorVariant
from utils.decorators import ajax_required


def get_order_from_cookie(cookies):
    # Get the cart items from cookies.
    cookie_order = cookies.get("order", "[]")

    # Get a queryset of products that client can access.
    products = ProductColorVariant.objects.filter(product__is_active=True)
    total_price = 0
    try:
        # Try to convert the order items to list.
        order = json.loads(cookie_order)
        items = []
        for item in order:
            # Search for the product.
            product_id = item["product"]
            product = products.filter(id=product_id).first()
            quantity = item["quantity"]
            # Validate the product and quantity,
            if product is not None and isinstance(quantity, int) \
                    and quantity and quantity <= product.stock_count:
                item["product"] = product
                total_price += product.get_final_price()
                items.append(item)
    except:
        items = []
    return items, total_price


class CartDetailView(View):
    def get(self, request):
        if request.user.is_authenticated:
            order, _ = Order.in_processes.get_or_create(user=request.user)
            items = order.items.all()
            items_count = order.items.count()
            total_price = order.get_final_price()
        else:
            items, total_price = get_order_from_cookie(request.COOKIES)
            items_count = len(items)
        context = {
            "items": items,
            "items_count": items_count,
            "total_price": total_price
        }

        return render(request, "orders/cart.html", context)


def render_colors(product_color_variant, user, cookies=None):
    context = {
        "product": product_color_variant.product,
        "selected_color": product_color_variant,
        "cookies": cookies,
        "user": user
    }
    return render_to_string("products/partials/colors.html",
                            context)


@require_GET
@ajax_required
def add_to_order_ajax(request):
    user = request.user
    # Get the all products that this client can access.
    if user.is_superuser:
        all_products = ProductColorVariant.objects.all()
    else:
        all_products = ProductColorVariant.objects.filter(
            product__is_active=True)

    # Try to get product id and quantity.
    try:
        product_id = request.GET.get("id")
        quantity = int(request.GET.get("quantity") or 1)
    except:
        return JsonResponse({"title": "خطایی رخ داد", "icon": "error"})

    if user.is_authenticated:
        # Try to get the user.
        try:
            product = all_products.get(id=product_id)
        except:
            return JsonResponse({"title": "محصول یافت نشد", "icon": "error"})
        # Validate the quantity.
        if quantity <= 0:
            return JsonResponse(
                {"title": "تعداد نامعتبر است", "icon": "error"})
        elif quantity > product.stock_count:
            return JsonResponse(
                {"title": "محصول به این تعداد موجود نمی باشد", "icon": "error"})
        # Get the current user cart or create it if it doesn't exist.
        order, created = Order.in_processes.get_or_create(user=user)
        # Get or create the cart item that is for founded product.
        order_item, created = OrderItem.objects.get_or_create(
            order=order, product=product)
        if created:
            colors = render_colors(product, request.user, request.COOKIES)
            return JsonResponse({
                "title": "محصول با موفقیت به سبد خرید اضافه گردید",
                "icon": "success", "items_count": str(order.items.count()),
                "colors": colors})
        else:
            order_item.quantity = quantity
            order_item.save()
            return JsonResponse(
                {"title": "تعداد محصول در سبد خرید با موفقیت تغییر یافت",
                     "icon": "success", "total_count": order.get_final_price()})
    else:
        # Get the cart items from cookies.
        cookie_order = request.COOKIES.get("order", "[]")
        try:
            # Try to convert the order items to list.
            order = list(json.loads(cookie_order))
            product = all_products.filter(id=product_id).first()
            if product is None:
                return JsonResponse({"title": "محصول یافت نشد", "icon": "error"})

            for item in order:
                # Search for the product.
                if product_id == item["product"]:
                    if 0 < quantity <= product.stock_count:
                        item["quantity"] = quantity
                        data = {
                            "title": "تعداد محصول در سبد خرید با موفقیت تغییر یافت",
                            "icon": "success"}
                        break
                    else:
                        data = {"title": "تعداد نامعتبر است", "icon": "error"}
            else:
                if 0 >= quantity:
                    data = {"title": "تعداد نامعتبر است", "icon": "error"}
                elif quantity > product.stock_count:
                    data = {"title": "محصول به این تعداد موجود نمی باشد", "icon": "error"}
                else:
                    item = {"product": product_id, "quantity": quantity}
                    order.append(item)
                    colors = render_colors(product, request.user, {"order": json.dumps(order)})
                    data = {
                            "title": "محصول با موفقیت به سبد خرید اضافه گردید",
                            "icon": "success", "items_count": len(order),
                            "colors": colors}
        except:
            data = {"title": "خطایی رخ داد", "icon": "error"}
        response = JsonResponse(data)
        response.set_cookie("order", json.dumps(order))
        return response


@require_GET
@ajax_required
def remove_from_order_ajax(request):
    user = request.user
    if user.is_superuser:
        all_products = ProductColorVariant.objects.all()
    else:
        all_products = ProductColorVariant.objects.filter(
            product__is_active=True)
    if user.is_authenticated:
        # Try to get the cart item and product.
        try:
            product_id = int(request.GET.get("id"))
            product = all_products.get(id=product_id)
            item = OrderItem.objects.get(
                order__is_paid=False, order__user=user, product_id=product_id)
        except:
            return JsonResponse({"title": "محصول یافت نشد", "icon": "error"})
        # Delete it.
        else:
            item.delete()
            colors = render_colors(product, request.user)
            return JsonResponse(
                {"title": "محصول با موفقیت از سبد خرید حذف شد",
                 "icon": "success", "colors": colors,
                 "items_count": str(item.order.items.count())})
    else:
        try:
            # Get the product.
            product_id = request.GET.get("id")
            product = all_products.filter(id=product_id).first()
            # If product doesn't found empty the order.
            if product:
                order: list = json.loads(request.COOKIES.get("order", "[]"))
            else:
                order = []
            for item in order:
                if item["product"] == product_id:
                    order.remove(item)
                    colors = render_colors(product, request.user, {"order": json.dumps(order)})
                    response = JsonResponse(
                        {"title": "محصول با موفقیت از سبد خرید حذف شد",
                         "icon": "success", "items_count": len(order),
                         "colors": colors})
                    response.set_cookie("order", json.dumps(order))
                    return response
            else:
                return JsonResponse({"title": "محصول یافت نشد", "icon": "error"})
        except:
            return JsonResponse({"title": "خطایی رخ داد", "icon": "error"})
