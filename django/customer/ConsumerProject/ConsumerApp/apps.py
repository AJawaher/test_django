from django.apps import AppConfig


class ConsumerAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ConsumerApp'

    def ready(self):
        import ConsumerApp.signals
