from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    phone = models.CharField("تلفن", max_length=11,
                             unique=True, blank=True, null=True)
    email = models.EmailField("ایمیل", unique=True)
    email_activation_code = models.PositiveSmallIntegerField(
        "کد فعال سازی حساب", blank=True, null=True)
    photo = models.ImageField(
        "تصویر", upload_to="accounts/images/", default="accounts/images/default-photo.png")
    address = models.TextField("آدرس", max_length=700, blank=True, null=True)

    is_active = models.BooleanField("فعال", default=False)
