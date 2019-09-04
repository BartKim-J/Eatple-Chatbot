#Django Library
from django.urls import reverse
from django.db import models
from django_mysql.models import Model

#External Library
import datetime

#Models 
from .models_config import Config

class User(models.Model):
    class Meta:
        ordering = ['-name']

    name             = models.CharField(max_length=Config.USER_NICKNAME_LENGTH, help_text="User Name")
    serial           = models.CharField(max_length=Config.USER_NICKNAME_LENGTH, help_text="User S/N")

    email            = models.CharField(max_length=Config.USER_NICKNAME_LENGTH, help_text="User ID")
    create_date      = models.DateTimeField(auto_now=True)

    def createUser(self, _name, _email):
        name  = _name
        email = _email
        self.save()
        return "{}".format(self.name)

            # Methods
    def __str__(self):
        return "{}".format(self.name)
