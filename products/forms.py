# Django
from django import forms

# Project
from .models import ProductComment


class ProductCommentForm(forms.ModelForm):
    class Meta:
        model = ProductComment
        fields = ["message", "rate", "parent"]

        error_messages = {
            "parent": {"invalid_choice": "پاسخ باید برای نظرهای این محصول درج شود."}
        }
