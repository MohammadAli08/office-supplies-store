# Django
import json
from django import template

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
    return json.loads(data)
