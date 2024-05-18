# Python
from typing import Any

# Django
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models.aggregates import Avg
from django.urls import reverse
from django.utils.text import slugify

# Project
from .deletion import SET_PARENT, SOFT_CASCADE
from accounts.models import User, Visitor

# Django Jalali
from django_jalali.db import models as jmodels
import jdatetime

# Color Field
from colorfield.fields import ColorField


# ---------------------managers--------------------- #

class AccessControlled(models.Manager):
    def access_level(self, user):
        if isinstance(user, User) and user.is_superuser:
            return self.get_queryset()
        else:
            return self.get_queryset().filter(is_active=True)


class UndeletedManager(jmodels.jManager):
    def get_queryset(self) -> models.QuerySet:
        queryset = self.model.SoftDeleteQueryset(self.model, using=self._db)
        return queryset.filter(is_deleted=False)


class DeletedManager(jmodels.jManager):
    def get_queryset(self) -> models.QuerySet:
        queryset = self.model.SoftDeleteQueryset(self.model, using=self._db)
        return queryset.filter(is_deleted=True)


# -------------------abstract models------------------- #

class SoftDelete(models.Model):
    is_deleted = models.BooleanField("حذف شده", default=False, editable=False)
    deleted_at = jmodels.jDateTimeField(
        "حذف شده در تاریخ", blank=True, null=True, editable=False)

    objects = UndeletedManager()

    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.deleted_at = jdatetime.datetime.now()
        self.save()

    class SoftDeleteQueryset(jmodels.jQuerySet):
        def delete(self):
            now = jdatetime.datetime.now()
            return self.update(is_deleted=True, deleted_at=now)

    class Meta:
        abstract = True


# ---------------------models--------------------- #

class Product(SoftDelete):
    title = models.CharField("عنوان", max_length=255)
    slug = models.SlugField("اسلاگ", max_length=255, blank=True, null=True)
    short_description = models.CharField("توضیحات کوتاه", max_length=350)
    long_description = models.TextField("توضیحات کامل")

    specification = models.JSONField(
        default=dict, blank=True, null=True, verbose_name="مشخصات فنی")

    weight = models.PositiveIntegerField("وزن")

    price = models.PositiveBigIntegerField("قیمت")
    discount = models.PositiveIntegerField("تخفیف", blank=True)

    main_image = models.ImageField("تصویر اصلی", upload_to="images/products/")

    created_at = jmodels.jDateTimeField("ایجاد شده در", auto_now_add=True)
    updated_at = jmodels.jDateTimeField("بروز‌رسانی شده در", auto_now=True)

    is_active = models.BooleanField("فعال", default=True)

    parent = models.ForeignKey(to="Category", on_delete=SET_PARENT, related_name="products",
                               blank=True, null=True, verbose_name="دسته بندی والد")
    visitors = models.ManyToManyField(
        to=Visitor, related_name="visited_products", blank=True, verbose_name="بازدید کننده ها")
    liked_by = models.ManyToManyField(
        to=User, related_name="liked_products", blank=True, verbose_name="پسندیده شده توسط")

    objects = UndeletedManager()
    access_controlled = AccessControlled()

    @property
    def final_price(self):
        return self.price - self.discount

    def get_rating_average(self, user=None, comments_queryset=None):
        if user:
            comments = ProductComment.access_control.access_level(user)
        else:
            comments = comments_queryset or ProductComment.objects
        return comments.filter(product=self).aggregate(average_rating=Avg("rate"))["average_rating"] or 5

    def get_color_variants(self):
        return self.product_color_variants.exclude(stock_count=0, color__color_name="_")

    def get_absolute_url(self):
        return reverse("products:detail", kwargs={"product_id": self.id})

    def save(self, *args, **kwargs) -> None:
        if not self.id:
            super().save(*args, **kwargs)
            self.slug = slugify(self.title+str(self.id), allow_unicode=True)
        return super().save()

    def __str__(self) -> str:
        return F"{self.title[:15]}..."

    class Meta:
        ordering = ["-created_at", "-updated_at"]
        indexes = [
            models.Index(fields=["id", "slug"]),
            models.Index(fields=["-created_at", "-updated_at"])
        ]
        verbose_name = "محصول"
        verbose_name_plural = "محصولات"


class DeletedProduct(Product):
    objects = DeletedManager()

    class Meta:
        proxy = True
        verbose_name = "محصول حذف شده"
        verbose_name_plural = "محصولات حذف شده"


class ProductColorVariant(SoftDelete):
    product = models.ForeignKey(
        to=Product, on_delete=SOFT_CASCADE, related_name="product_color_variants", verbose_name="محصول")
    color = models.ForeignKey(
        to="Color", on_delete=SOFT_CASCADE, related_name="product_color_variants", verbose_name="رنگ")

    price = models.PositiveBigIntegerField("قیمت", blank=True, null=True)
    discount = models.PositiveIntegerField("تخفیف", blank=True, null=True)
    stock_count = models.PositiveIntegerField("تعداد موجودی")

    objects = UndeletedManager()

    def get_price(self):
        return self.price or self.product.price

    def get_discount(self):
        return self.discount or self.product.discount

    def get_final_price(self):
        return self.get_price() - self.get_discount()

    def get_absolute_url(self):
        return self.product.get_absolute_url()

    def __str__(self) -> str:
        return f"{self.product}-{self.color}"

    class Meta:
        verbose_name = "نوع رنگی محصول"
        verbose_name_plural = "نوع های رنگی محصولات"


class DeletedProductColorVariant(ProductColorVariant):
    objects = DeletedManager()

    class Meta:
        proxy = True
        verbose_name = "نوع رنگی محصول حذف شده"
        verbose_name_plural = "نوع رنگی های محصولات حذف شده"


class Color(models.Model):
    COLOR_PALETTE = [
        ("#000000", "سیاه"),
        ("#FFFFFF", "سفید"),
        ("#FF0000", "قرمز"),
        ("#0000FF", "آبی"),
        ("#008000", "سبز"),
        ("#FFFF00", "زرد"),
        ("#FFA500", "نارنجی"),
        ("#800080", "بنفش"),
        ("#FFC0CB", "صورتی"),
        ("#964B00", "قهوه ای"),
        ("#808080", "طوسی"),
    ]
    color_name = models.CharField(
        max_length=300, verbose_name="نام رنگ")
    color_hex_code = ColorField(
        samples=COLOR_PALETTE, verbose_name="کد hex رنگ")
    products = models.ManyToManyField(
        to=Product, through=ProductColorVariant, related_name="color_variants", verbose_name="رنگ ها"
    )

    def __str__(self) -> str:
        return str(self.color_name)

    class Meta:
        verbose_name = "رنگ محصول"
        verbose_name_plural = "رنگ های محصول"


class ProductGallery(models.Model):
    product = models.ForeignKey(
        to=Product, on_delete=models.CASCADE, related_name="images", verbose_name="محصول")
    image = models.ImageField(verbose_name="تصویر",
                              upload_to="images/products/")

    def __str__(self) -> str:
        return F"{self.id}-{self.product}"

    class Meta:
        verbose_name = "گالری محصول"
        verbose_name_plural = "گالری های محصول"


class ProductComment(models.Model):
    message = models.TextField("پیام")
    rate = models.PositiveSmallIntegerField(
        "نمره", validators=[MinValueValidator(1), MaxValueValidator(5)], blank=True, null=True)

    user = models.ForeignKey(
        to=User, on_delete=models.CASCADE, related_name="comments", verbose_name="کاربر")
    parent = models.ForeignKey(
        to="self", on_delete=models.CASCADE, related_name="answers", blank=True, null=True, verbose_name="والد")
    product = models.ForeignKey(
        to=Product, on_delete=models.CASCADE, related_name="comments", verbose_name="محصول")

    created_at = jmodels.jDateTimeField("تاریخ ایجاد", auto_now_add=True)

    is_active = models.BooleanField("فعال", default=True)

    objects = jmodels.jManager()
    access_control = AccessControlled()

    def clean(self) -> None:
        if self.rate and self.parent:
            raise ValidationError(
                {"rate": "یک نظر همزمان نمی تواند هم پاسخ باشد و هم نمره داشته باشد."})
        elif not (self.rate or self.parent):
            raise ValidationError(
                {"rate": "نمره را وارد کنید."})
        else:
            return super().clean()

    def get_answers(self, user=None, comments_queryset=None):
        """
        Return all of the answers of a comment based on 
        user permissions or comments_queryset.
        """
        all_comments = comments_queryset or ProductComment.access_control.access_level(
            user)
        return all_comments.filter(parent=self)

    def __str__(self) -> str:
        return F"{str(self.user)}-{str(self.product)}"

    class Meta:
        verbose_name = "نظر محصول"
        verbose_name_plural = "نظرات محصول"

        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"])
        ]


class Category(models.Model):
    title = models.CharField("عنوان", max_length=225)
    image = models.ImageField(verbose_name="تصویر",
                              upload_to="images/categories/")

    parent = models.ForeignKey(
        to="self", on_delete=SET_PARENT, related_name="subsets", verbose_name="والد", blank=True, null=True)
    is_active = models.BooleanField("فعال", default=True)

    objects = AccessControlled()

    def delete(self, using: Any = ..., keep_parents: bool = ...) -> tuple[int, dict[str, int]]:
        storage, path = self.image.storage, self.image.path
        storage.delete(path)
        return super().delete(using, keep_parents)

    def get_subset_products(self, products_queryset=Product.objects):
        def get_subset_ids(category):
            ids = [category.id]
            for sub_category in category.subsets.all():
                ids.extend(get_subset_ids(sub_category))
            return ids

        return products_queryset.filter(parent_id__in=get_subset_ids(self))

    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = "دسته بندی"
        verbose_name_plural = "دسته بندی ها"
