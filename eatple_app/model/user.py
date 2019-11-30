'''
    Author : Ben Kim

    @NOTE
    @BUG
    @TODO
 
'''
# Django Library
from eatple_app.models import Store, Menu
from eatple_app.models import Category, Tag
from eatple_app.models import Order
from django.urls import reverse
from django.db import models
from django_mysql.models import Model

# External Library
from phonenumber_field.modelfields import PhoneNumberField

# Define
from eatple_app.define import *

class User(models.Model):
    class Meta:
        ordering = ['-nickname']

    nickname = models.CharField(
        max_length=USER_NICKNAME_LENGTH, null=True)

    profile_image_url = models.CharField(
        max_length=STRING_LENGTH, null=True)
    
    phone_number = PhoneNumberField(
        max_length=STRING_LENGTH, null=True)

    email = models.CharField(
        max_length=STRING_LENGTH, null=True)

    birthyear = models.CharField(
        max_length=STRING_LENGTH, null=True)
    birthday = models.CharField(
        max_length=STRING_LENGTH, null=True)
    
    gender = models.CharField(
        max_length=STRING_LENGTH, null=True)
    
    ci = models.CharField(
        max_length=STRING_LENGTH, null=True)
    ci_authenticated_at = models.CharField(
        max_length=STRING_LENGTH, null=True )
    
    app_user_id = models.IntegerField(default=0)
    
    create_date = models.DateTimeField(auto_now=True)

    @classmethod
    def signUp(cls, *args, **kwargs):
        registedUser = cls(*args, **kwargs)
        registedUser.save()

        return registedUser

    # Methods
    def __str__(self):
        return "{}".format(self.app_user_id)
