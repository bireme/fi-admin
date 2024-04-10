# apps.py
from django.apps import AppConfig

class UtilsAppConfig(AppConfig):
    name = 'utils'

    def ready(self):
        import utils.signals
