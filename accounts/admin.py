from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["username", "email", "email_activation_code", "is_active", "is_staff", "is_superuser"]
    list_editable = ["email", "email_activation_code", "is_active", "is_staff", "is_superuser"]
    list_filter = ["is_active", "is_staff", "is_superuser"]
    search_fields = ["username", "email", "phone", "address"]