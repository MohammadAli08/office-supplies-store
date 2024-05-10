# Django
from django.shortcuts import render
from django.views.decorators.http import require_GET


@require_GET
def index(request):
    return render(request, "home/index.html")


@require_GET
def header(request):
    return render(request, "components/header.html")


@require_GET
def footer(request):
    return render(request, "components/footer.html")
