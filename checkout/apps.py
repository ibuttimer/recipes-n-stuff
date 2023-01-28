from django.apps import AppConfig

from .constants import THIS_APP

class CheckoutConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = THIS_APP
