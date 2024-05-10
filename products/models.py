# Django
from django.db import models

# Project
from .deletion import SET_PARENT
from accounts.models import User


class AccessControlled(models.Manager):
    def access_level(self, user):
        if isinstance(user, User) and user.is_superuser:
            return self.get_queryset()
        else:
            return self.get_queryset().filter(is_active=True)


class Category(models.Model):
    title = models.CharField("عنوان", max_length=225)
    image = models.ImageField(verbose_name="تصویر",
                              upload_to="categories/images/")

    parent = models.ForeignKey(
        to="self", on_delete=SET_PARENT, related_name="subsets", verbose_name="والد")
    is_active = models.BooleanField("فعال", default=True)

    objects = AccessControlled()

    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = "دسته بندی"
        verbose_name_plural = "دسته بندی ها"
