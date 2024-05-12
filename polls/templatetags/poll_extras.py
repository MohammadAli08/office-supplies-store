# Django
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
