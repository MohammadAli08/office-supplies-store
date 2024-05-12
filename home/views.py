# Django
from django.shortcuts import render
from django.views.decorators.http import require_GET

# Project
from products.models import Product

@require_GET
def index(request):
    latest_products = Product.objects.all()[:8]
    context = {
        "latest_products": latest_products
    }
    return render(request, "home/index.html", context)


@require_GET
def header(request):
    return render(request, "components/header.html")


@require_GET
def footer(request):
    return render(request, "components/footer.html")
