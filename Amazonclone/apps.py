from django.apps import AppConfig

class AmazoncloneConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Amazonclone'

    def ready(self):
        import Amazonclone.signals