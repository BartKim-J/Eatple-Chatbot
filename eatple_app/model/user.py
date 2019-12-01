# define
from eatple_app.define import *
# Django Library
from django.db import models
from django.conf import settings
from django.urls import reverse
from django.core.files.storage import FileSystemStorage
from django_mysql.models import Model
from django.core.validators import MaxValueValidator, MinValueValidator
from django import forms

# Utils
from eatple_app.model.utils import OverwriteStorage
from eatple_app.model.utils import logo_directory_path

class KakaoUser(models.Model):
    nickname = models.CharField(
    max_length=USER_NICKNAME_LENGTH, null=True)

    profile_image_url = models.CharField(
        max_length=WORD_LENGTH, null=True)
    
    phone_number = PhoneNumberField(
        max_length=WORD_LENGTH, null=True)

    email = models.CharField(
        max_length=WORD_LENGTH, null=True)

    birthyear = models.CharField(
        max_length=WORD_LENGTH, null=True)
    birthday = models.CharField(
        max_length=WORD_LENGTH, null=True)
    
    gender = models.CharField(
        max_length=WORD_LENGTH, null=True)
    
    ci = models.CharField(
        max_length=STRING_LENGTH, null=True)
    ci_authenticated_at = models.CharField(
        max_length=STRING_LENGTH, null=True )
    
    app_user_id = models.IntegerField(default=0)

    class Meta:
        abstract = True

class User(KakaoUser, models.Model):
    class Meta:
        ordering = ['-nickname']
    
    create_date = models.DateTimeField(auto_now=True)

    @classmethod
    def signUp(cls, *args, **kwargs):
        registedUser = cls(*args, **kwargs)
        registedUser.save()

        return registedUser

    # Methods
    def __str__(self):
        return "{}".format(self.app_user_id)
