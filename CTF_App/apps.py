from django.apps import AppConfig


class CtfAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'CTF_App'

    def ready(self):
        import CTF_App.signals
