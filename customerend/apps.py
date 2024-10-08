from django.apps import AppConfig


class CustomerendConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "customerend"

    def ready(self):
        import customerend.signals
