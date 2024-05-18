"""
Override the createsuperuser command to validate email uniqueness.
"""

from django.contrib.auth.management.commands import createsuperuser
from django.db.models import EmailField

from accounts.models import User


class Command(createsuperuser.Command):
    def get_input_data(self, field, message, default=None, *args, **kwargs):
        val = super().get_input_data(field, message, default)
        if type(field) == EmailField and val:
            if User.objects.filter(email=val).exists():
                self.stderr.write("Error: این ایمیل از قبل گرفته شده است.")
                return
        return val
