#Django Library
from django.urls import reverse
from django.db import models
from django_mysql.models import Model

#External Library

#Models 
from .models_config import Config

#GLOBAL CONFIG
NOT_APPLICABLE          = Config.NOT_APPLICABLE
DEFAULT_OBJECT_ID       = Config.DEFAULT_OBJECT_ID

USER_NICKNAME_LENGTH    = Config.USER_NICKNAME_LENGTH
USER_ID_CODE_LENGTH    = Config.USER_ID_CODE_LENGTH

#STATIC CONFIG

class User(models.Model):
    class Meta:
        ordering = ['-name']

    name             = models.CharField(max_length=USER_NICKNAME_LENGTH, help_text="User Name")
    identifier_code  = models.CharField(max_length=USER_ID_CODE_LENGTH, help_text="User ID", default='')

    create_date      = models.DateTimeField(auto_now=True)

    @classmethod
    def registerUser(cls, _name, _identifier_code):
        registedUser = cls(name=_name, identifier_code=_identifier_code)
        registedUser.save();

        return registedUser

            # Methods
    def __str__(self):
        return "{}".format(self.name)
