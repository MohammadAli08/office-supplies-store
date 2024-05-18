# Django
import json
from django import template

# Project
from accounts.models import User
from orders.views import get_order_from_cookie
from products.models import Product

register = template.Library()


@register.simple_tag()
def products_count(category, user):
    products = Product.access_controlled.access_level(user)
    count = products.filter(parent=category).count()
    for sub_category in category.subsets.all():
        count += products_count(sub_category, user)
    return count


@register.simple_tag()
def rating_percents(comments):
    """Get rating percent of each rate between 1 and 5"""
    percents = []
    count = comments.filter(parent__isnull=True).count()
    try:
        for rating_number in range(1, 6):
            percents.append(int((comments.filter(
                rate=rating_number).count() / count * 100)))
    except ZeroDivisionError:
        return 0
    return percents


@register.simple_tag()
def call_method(obj, method_name, *args, **kwargs):
    """A safe template tag to call some specified methods"""
    if method_name in ["get_rating_average", "get_answers"]:
        return getattr(obj, method_name)(*args, **kwargs)
    else:
        raise ValueError(f"invalid method_name: {method_name}")


@register.filter()
def loads(data):
    try:
        return json.loads(data)
    except:
        return data


@register.simple_tag()
def get_order_item_quantity(product, user, cookies):
    if isinstance(user, User):
        item = product.order_items.filter(
            order__is_paid=False, order__user=user).first()
        return item.quantity if item else 0
    else:
        items, _ = get_order_from_cookie(cookies=cookies)
        for item in items:
            if item["product"] == product:
                return item["quantity"]
        else:
            return 0
