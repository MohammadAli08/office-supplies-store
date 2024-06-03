from django.apps import AppConfig


class UserPanelsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'user_panels'

    verbose_name = "پنل کاربری"
    verbose_name_plural = "پنل های کاربری"
