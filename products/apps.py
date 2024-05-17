from django.apps import AppConfig


class ProductsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'products'

    verbose_name = "محصول"
    verbose_name_plural = "محصولات"

    def ready(self) -> None:
        import products.signals
