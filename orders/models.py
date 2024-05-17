# Django
from django.db import models

# Project
from accounts.models import User
from products.models import ProductColorVariant

# Django jalali
from django_jalali.db import models as jmodels


class Order(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.SET_NULL,
                             related_name="orders", null=True, blank=False, verbose_name="کاربر")
    first_name = models.CharField("نام", max_length=150, blank=True, null=True)
    last_name = models.CharField(
        "نام خانوادگی", max_length=150, blank=True, null=True)
    phone = models.CharField("تلفن", max_length=11, blank=True, null=True)
    postal_code = models.CharField(
        "کد پستی", max_length=10, blank=True, null=True)
    address = models.TextField("آدرس", max_length=700, blank=True, null=True)

    is_paid = models.BooleanField("پرداخت شده", default=False)
    payment_date = jmodels.jDateTimeField("زمان پرداخت", blank=True, null=True)

    objects = jmodels.jManager()

    def get_final_price(self):
        total = 0
        for item in self.items.all():
            total += item.get_final_price()
        return total

    def __str__(self) -> str:
        return f"{self.user}-{self.is_paid}-{self.id}-cart"

    class Meta:
        verbose_name = "سبد خرید"
        verbose_name_plural = "سبدهای خرید"

        indexes = (
            models.Index(fields=["is_paid", "-payment_date"]),
        )
        ordering = (
            "is_paid", "-payment_date"
        )


class OrderItem(models.Model):
    order = models.ForeignKey(to=Order, on_delete=models.CASCADE,
                              related_name="items", verbose_name="سفارش")
    product = models.ForeignKey(to=ProductColorVariant, on_delete=models.deletion.CASCADE,
                                related_name="order_items", verbose_name="نوع رنگی محصول")

    quantity = models.PositiveIntegerField("تعداد", default=1)

    paid_price = models.PositiveBigIntegerField(
        "قیمت پرداخت شده", blank=True, null=True)
    discount = models.PositiveBigIntegerField("تخفیف", blank=True, null=True)

    def get_final_price(self):
        return self.quantity * (self.paid_price or self.product.get_final_price())

    def __str__(self) -> str:
        return str(self.product) + str(self.order)

    class Meta:
        verbose_name = "محصول سبد خرید"
        verbose_name_plural = "محصولات سبد خرید"
