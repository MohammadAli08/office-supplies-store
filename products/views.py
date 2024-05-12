# Django
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.generic import View
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.decorators import method_decorator
from django.template.loader import render_to_string
from django.views.decorators.http import require_GET

# Project
from . import models
from utils.decorators import ajax_required


def category_filter(request, categories_queryset, products_queryset=None):
    """Filter products based on selected category"""
    # Get the selected category id.
    category_id = request.GET.get("category_id")
    if category_id and not category_id.isdigit():
        raise Http404("دسته بندی یافت نشد")

    # Did user select any categories?
    if category_id:
        # Find category or raise http404 error.
        category = get_object_or_404(categories_queryset, id=category_id)
        categories = [category]
        # Get the parents categories of selected category.
        while parent := category.parent:
            if parent in categories_queryset:
                categories.insert(0, parent)
            else:
                # Raise http404 error if user can't access to the parent category.
                raise Http404("دسته بندی یافت نشد")
            category = parent
        # Get the subset products of selected category.
        products = categories[-1].get_subset_products(products_queryset)
        return products, categories
    else:
        return products_queryset or models.Product.objects.all(), categories_queryset


def price_filter(request, products, max_price):
    """Filter the products based on entered price range"""
    # Try to get the price range.
    try:
        start_price = int(request.GET.get("start_price", 0))
        end_price = int(request.GET.get("end_price", max_price))
    # Return all products without filtering if the type of
    # entered prices is wrong.
    except:
        return products, 0, max_price
    # Return the filtered products every thing is correct.
    else:
        products = [product for product in products if start_price <=
                    product.final_price <= end_price]
        return products, start_price, end_price


def sort_products(request, products):
    """Sort the products queryset based on user selected ordering"""
    # Get the sort by from user selected options.
    sort_by = request.GET.get("sort_by", "newest")
    reverse = False
    # Convert sorting title to functionality.
    match sort_by:
        case "newest":
            def order_by(product): return product.created_at
            reverse = True
        case "cheapest":
            def order_by(product): return product.final_price
        case "most-expensive":
            def order_by(product): return product.final_price
            reverse = True
        case "most-rating":
            def order_by(product): return product.rating_number
            reverse = True
        case "most-popular":
            def order_by(product): return product.liked_by.count()
            reverse = True
        case "most-visited":
            def order_by(product): return product.visitors.count()
            reverse = True
        case _:
            def order_by(product): return product.created_at
            reverse = True

    # Return the sorted products.
    return sorted(products, key=order_by, reverse=reverse)


def paginate_products(request, products):
    """Paginate products based on user choices"""
    # Get per page from user and validate it.
    per_page = request.GET.get("per_page")
    if per_page not in ["9", "15", "30"]:
        per_page = 9
    page_number = request.GET.get("page", 1)

    # Create Paginator object.
    paginator = Paginator(products, per_page)
    # Get the selected page.
    try:
        page_obj = paginator.get_page(page_number)
    except EmptyPage:
        page_obj = paginator.get_page(paginator.num_pages)
    except PageNotAnInteger:
        page_obj = paginator.get_page(1)

    return page_obj, per_page


def filter_data(request):
    """
    Filter the products based on user permissions and selected filters.
    """
    # Get products and categories that user can access.
    products_queryset = models.Product.access_controlled.access_level(
        request.user)
    categories = models.Category.objects.access_level(request.user)

    products, categories = category_filter(
        request, categories, products_queryset)

    try:
        # Try to find the maximum price from the filtered products.
        max_price = sorted(
            products, key=lambda product: product.price, reverse=True)[0].price
    except:
        # If there is no product to find the maximum price Try
        # to get it from base products(products_queryset).
        try:
            max_price = products_queryset.order_by("-price").first().price
        except:
            # Set the max price to 100 as the default if there was no
            # product yet to set the maximum price.
            max_price = 100

    products, start_price, end_price = price_filter(
        request, products, max_price)

    # Sort the products.
    products = sort_products(request, products)

    # Paginate the products.
    paginated_products, per_page = paginate_products(request, products)

    return {
        "categories": categories, "max_price": max_price,
        "paginated_products": paginated_products, "per_page": per_page,
        "start_price": start_price, "end_price": end_price
    }


@method_decorator(require_GET, "dispatch")
class ProductListView(View):
    def get(self, request):
        context = filter_data(request)
        return render(request, "products/product_list.html", context)


@method_decorator((ajax_required, require_GET), "dispatch")
class ProductListFilterAjaxView(View):
    def get(self, request):
        response = filter_data(request)
        data = {}
        if request.GET.get("category_changed") == "true":
            data["categories"] = render_to_string(
                "products/partials/categories.html", {"categories": response["categories"]}, request)

        paginated_products = response["paginated_products"]

        data["products"] = render_to_string(
            "products/partials/product_partials.html", {"paginated_products": paginated_products}, request)
        data["pagination"] = render_to_string(
            "products/partials/pagination.html", {"page_obj": paginated_products})
        data["price_filter"] = render_to_string(
            "products/partials/price_filter.html", {
                "start_price": response["start_price"],
                "end_price": response["end_price"],
                "max_price": response["max_price"]
            }
        )

        return JsonResponse(data)
