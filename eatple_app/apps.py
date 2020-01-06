# Django Library
from django.apps import AppConfig
from suit.apps import DjangoSuitConfig

# App Config

class SuitConfig(DjangoSuitConfig):
    layout = 'horizontal'
    
class EatpleChatbotAppConfig(AppConfig):
    name = 'eatple_app'
    
    verbose_name = '잇플 DB'