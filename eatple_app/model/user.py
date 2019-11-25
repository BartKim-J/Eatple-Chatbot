'''
    Author : Ben Kim

    @NOTE
    @BUG
    @TODO
 
'''
# Django Library
from eatple_app.models import Store, Menu
from eatple_app.models import Category, SubCategory
from eatple_app.models import Order
from django.urls import reverse
from django.db import models
from django_mysql.models import Model

# External Library

# Define
from eatple_app.define import EP_define

NOT_APPLICABLE = EP_define.NOT_APPLICABLE
DEFAULT_OBJECT_ID = EP_define.DEFAULT_OBJECT_ID

USER_NICKNAME_LENGTH = EP_define.USER_NICKNAME_LENGTH
USER_ID_CODE_LENGTH = EP_define.USER_ID_CODE_LENGTH

# Other Models

# Models


class UserFlags(models.Model):
    class Meta:
        ordering = ['-name']

    name = models.CharField(max_length=USER_NICKNAME_LENGTH, help_text="Flag")
    active = models.BooleanField(default=False)

    # Methods
    def __str__(self):
        return "{}".format(self.name)


class User(models.Model):
    class Meta:
        ordering = ['-name']

    name = models.CharField(
        max_length=USER_NICKNAME_LENGTH, help_text="User Name")

    identifier_code = models.CharField(
        max_length=USER_ID_CODE_LENGTH, help_text="User ID", default='')

    create_date = models.DateTimeField(auto_now=True)

    @classmethod
    def registerUser(cls, _name, _identifier_code):
        registedUser = cls(name=_name, identifier_code=_identifier_code)
        registedUser.save()

        return registedUser

    # Methods
    def __str__(self):
        return "{}".format(self.name)
