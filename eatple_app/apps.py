# Django Library
from django.apps import AppConfig
from suit.apps import DjangoSuitConfig

# App Config

class SuitConfig(DjangoSuitConfig):
    layout = 'horizontal'
    
class EatplusChatbotAppConfig(AppConfig):
    name = 'eatple_app'
