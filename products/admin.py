# Django
from typing import Any
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http import HttpRequest

# Project
from .models import (
    Category, DeletedProductColorVariant, Product, ProductColorVariant,
    Color, ProductGallery, ProductComment,
    DeletedProduct
)


# inline admins.
class ProductColorVariantInline(admin.TabularInline):
    model = ProductColorVariant


class DeletedProductColorVariantInline(admin.TabularInline):
    model = DeletedProductColorVariant
    can_delete = False


class ProductGalleryInline(admin.TabularInline):
    model = ProductGallery


class ProductCommentInline(admin.TabularInline):
    model = ProductComment
    readonly_fields = ["created_at"]



# model admins.

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["short_title", "parent", "price", "discount", "is_active"]
    list_editable = ["price", "discount", "is_active"]
    list_filter = ["parent", "is_active"]
    readonly_fields = ["created_at", "updated_at", "slug"]
    date_hierarchy = "created_at"
    search_fields = ["title", "short_description", "long_description"]
    raw_id_fields = ["parent", "visitors", "liked_by"]

    inlines = [
        ProductColorVariantInline,
        ProductGalleryInline,
        ProductCommentInline
    ]

    def short_title(self, obj):
        return obj.title[:20] + "..."


@admin.register(DeletedProduct)
class DeletedProductAdmin(ProductAdmin):
    actions = ["recover_items"]
    inlines = [
        DeletedProductColorVariantInline,
    ]

    @admin.action(description="بازگردانی محصولات حذف شده")
    def recover_items(self, request, queryset):
        for product in queryset:
            color_variants = DeletedProductColorVariant.objects.filter(
                product=product)
            color_variants.update(is_deleted=False, deleted_at=None)
        queryset.update(is_deleted=False, deleted_at=None)


@admin.register(ProductColorVariant)
class ProductColorVariantAdmin(admin.ModelAdmin):
    list_display = ["product", "color", "price", "discount"]
    list_editable = ["price", "discount"]
    list_filter = ["color"]
    search_fields = ["product", "color"]
    raw_id_fields = ["product", "color"]


@admin.register(DeletedProductColorVariant)
class DeletedProductColorVariantAdmin(admin.ModelAdmin):
    actions = ["recover_items"]
    list_display = ["product", "color", "price", "discount"]
    list_editable = ["price", "discount"]
    list_filter = ["color"]
    search_fields = ["product", "color"]
    raw_id_fields = ["product", "color"]

    @admin.action(description="بازگردانی نوع های رنگی محصول حذف شده")
    def recover_items(self, request, queryset):
        queryset.update(is_deleted=False, deleted_at=None)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["title", "is_active"]
    list_editable = ["is_active"]
    list_display_links = ["title"]
    list_filter = ["parent", "is_active"]
    search_fields = ["title"]
    raw_id_fields = ["parent"]


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ["color_name", "color_hex_code"]
    list_editable = ["color_hex_code"]
    list_filter = ["color_name"]
    search_fields = ["color_name", "products", "color_hex_code"]
    raw_id_fields = ["products"]
