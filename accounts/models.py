# Python
import random

# Django
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

# Project
from utils.email import send_email


class User(AbstractUser):
    phone = models.CharField("تلفن", max_length=11,
                             unique=True, blank=True, null=True)
    email = models.EmailField("ایمیل", unique=True)
    email_activation_code = models.PositiveIntegerField(
        "کد فعال سازی حساب", blank=True, null=True)
    photo = models.ImageField(
        "تصویر", upload_to="images/accounts/", default="images/accounts/default-photo.png")
    address = models.TextField("آدرس", max_length=700, blank=True, null=True)

    is_active = models.BooleanField("فعال", default=False)

    def __str__(self) -> str:
        return self.username

    def send_email_activation_code(self, using_time):
        """Generate a new activation code and send an email to give that to user"""
        # Generate an email activation code for validating the inputted email.
        while True:
            code = random.randint(100000, 999999)
            if not User.objects.filter(email_activation_code=code).exists():
                break
        self.email_activation_code = code

        # send the email activation code to user.
        send_email("فعال سازی حساب", [self.email],
                   "accounts/emails/activation_code.html", {"user": self, "using_time": using_time})

        # Set the last login time to have the activation code sent time.
        self.last_login = timezone.now()

        # Save the user instance on database.
        self.save()

    class Meta:
        verbose_name = "کاربر"
        verbose_name_plural = "کاربران"


class Visitor(models.Model):
    user = models.OneToOneField(
        to=User, on_delete=models.SET_NULL, related_name="viewer", blank=True, null=True, editable=False)
    ip = models.GenericIPAddressField(
        "آی‌پی", blank=True, null=True, editable=False)
