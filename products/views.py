# Django
import json
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_GET
from django.views.generic import View

from accounts.models import Visitor
from utils.http import get_visitor_ip

# Project
from . import models
from .forms import ProductCommentForm
from utils.decorators import ajax_required


# ----------------------product list----------------------

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
            def order_by(product): return product.get_rating_average()
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


class ProductListView(View):
    def get(self, request):
        context = filter_data(request)
        return render(request, "products/product_list.html", context)


@method_decorator(ajax_required, "dispatch")
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


# ---------------------product detail---------------------

def get_common_data(user, product_id):
    """
    Find and return all common data that used in product
    details pages.
    """

    # Find all products and comments that this user can access.
    all_products = models.Product.access_controlled.access_level(
        user)
    all_comments = models.ProductComment.access_control.access_level(
        user)

    # Find the selected product and its comments.
    product = get_object_or_404(all_products, id=product_id)
    product_comments = all_comments.filter(product=product)

    # Get the comments that doesn't have parent comment.
    product_main_comments = product_comments.filter(parent__isnull=True)
    # paginate them.
    paginator = Paginator(product_main_comments, 5)

    return paginator, product, product_comments, product_main_comments


@method_decorator((login_required), "post")
class ProductDetailView(View):
    def get(self, request, product_id):
        context = self.get_context_data(product_id)
        context["form"] = ProductCommentForm()
        product = context["product"]
        if request.user.is_authenticated:
            visitor, _ = Visitor.objects.get_or_create(user=request.user)
            visitor.ip = get_visitor_ip(request)
        else:
            visitor, _ = Visitor.objects.get_or_create(
                ip=get_visitor_ip(request))
        visitor.save()
        product.visitors.add(visitor)
        return render(request, "products/product_detail.html", context)

    def post(self, request, product_id):
        """Create comments.

        Hints:
        Comments can only be created as an original comment or as a reply.
        Replies can only be added to the original comment, not to comments
        that are replies.
        """

        context = self.get_context_data(product_id)

        # Fill the form with submitted data.
        form = ProductCommentForm(request.POST)
        # Validate the form.
        if form.is_valid():
            # Save the comment without saving on database to get the instance.
            comment = form.save(commit=False)
            product = context["product"]

            # Validate parent comment.
            if parent := comment.parent:
                # Is the parent comment of the parent field a main comment?
                if parent.parent is not None:
                    form.add_error(
                        "parent", "پاسخ تنها می تواند برای نظرات اصلی درج شود.")

                # Is the parent comment for this product?
                elif parent not in context["all_comments"]:
                    form.add_error(
                        "parent", "پاسخ باید برای نظرهای این محصول درج شود.")
            # Set product and user of this comment.
            comment.product = product
            comment.user = request.user

            # Save comment on database.
            comment.save()
            messages.success(request, "نظر شما با موفقیت ثبت شد")

            # Update the context data.
            context = self.get_context_data(product_id)

            # Create an empty form.
            form = ProductCommentForm()

        context["form"] = form
        return render(request, "products/product_detail.html", context)

    def get_context_data(self, product_id):
        common_data = get_common_data(self.request.user, product_id)
        paginator, product, product_comments, product_main_comments = common_data

        paginated_comments = paginator.get_page(1)
        return {
            "product": product,
            "paginated_comments": paginated_comments,
            "all_comments": product_comments,
            "comments_count": product_main_comments.count()
        }


@require_GET
@ajax_required
def get_comments(request, product_id, page):
    """
    Get more comments to show to user.
    """
    paginator, *_ = get_common_data(request.user, product_id)
    try:
        paginated_comments = paginator.get_page(page)
    except:
        pass
    else:
        rendered_comments = render_to_string("products/partials/comments.html",
                                             {"paginated_comments": paginated_comments}, request)
        return JsonResponse({"comments": rendered_comments})


@ajax_required
def like_or_dislike_ajax(request, product_id):
    """
    Change the liked products to disliked products and vice versa.
    If user is authenticated the liked products will add to the
    liked_products field But otherwise, the liked products are
    stored on cookies.
    """

    # Get the user.
    user = request.user
    # Get the product based on user permission.
    all_products = models.Product.access_controlled.access_level(user)
    product = get_object_or_404(all_products, id=product_id)

    # Set a default value for data.
    data = {"success": "محصول با موفقیت به لیست علاقه مندی ها افزوده شد",
            "is_liked": "true"}
    if user.is_authenticated:
        # If the user already exists in the product's liked by, remove it.
        if user in product.liked_by.all():
            product.liked_by.remove(user)
            data = {"success": "محصول با موفقیت از لیست علاقه مندی ها حذف شد"}
        # If user doesn't exist in products's liked by, add it.
        else:
            product.liked_by.add(user)

        # Create the response.
        response = JsonResponse(data)
    else:
        # Get the current liked products list from cookies.
        liked_products_cookie = request.COOKIES.get("liked_products", "[]")

        # Try to converts them to list.
        try:
            liked_products: list = json.loads(liked_products_cookie)
        # Set a blank list for liked_products if there is an exception.
        except:
            liked_products = []
        # If product already exists in user liked products, Remove it.
        if product_id in liked_products:
            liked_products.remove(product_id)
            data = {"success": "محصول با موفقیت از لیست علاقه مندی ها حذف شد"}
        # If product doesn't exist in user liked products, Add it.
        else:
            liked_products.append(product_id)
        # Create the response.
        response = JsonResponse(data)
        # Set the user liked products on cookies.
        response.set_cookie("liked_products", json.dumps(liked_products))
    return response
