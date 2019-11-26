
from django.db import models
from django.conf import settings
from django.urls import reverse
from django.core.files.storage import FileSystemStorage
from django_mysql.models import Model
from django.core.validators import MaxValueValidator, MinValueValidator


import os
from random import *

# Utils
from eatple_app.model.utils import OverwriteStorage
from eatple_app.model.utils import logo_directory_path

# define
from eatple_app.define import EP_define

NOT_APPLICABLE = EP_define.NOT_APPLICABLE
DEFAULT_OBJECT_ID = EP_define.DEFAULT_OBJECT_ID

STRING_LENGTH = EP_define.STRING_LENGTH
WORD_LENGTH = EP_define.WORD_LENGTH

LUNCH_PICKUP_TIME = EP_define.LUNCH_PICKUP_TIME
DINNER_PICKUP_TIME = EP_define.DINNER_PICKUP_TIME


def getUniqueID(instance):
    return "{:4d}".format(instance.id)

# Models


class StoreInfo(models.Model):
    store_id = models.CharField(default="Store ID",
                            max_length=STRING_LENGTH, help_text="Store ID")
    
    name = models.CharField(default="Store Name",
                            max_length=STRING_LENGTH, help_text="Store Name")
    
    addr = models.CharField(
        default="Address", max_length=STRING_LENGTH, help_text="Address")
    owner = models.CharField(
        default="Owner", max_length=WORD_LENGTH, help_text="Owner")
    description = models.TextField(
        default="Store Dscription", help_text="Store Dscription")

    logo = models.ImageField(default="STORE_DB/images/default/logoImg.png",
                             blank=True, upload_to=logo_directory_path, storage=OverwriteStorage())

    class Meta:
        abstract = True


class StoreSetting(models.Model):
    lunch_pickupTime_start = models.IntegerField(
        default=0, choices=LUNCH_PICKUP_TIME, help_text="")

    lunch_pickupTime_end = models.IntegerField(default=len(
        LUNCH_PICKUP_TIME) - 1, choices=LUNCH_PICKUP_TIME, help_text="")

    dinner_pickupTime_start = models.IntegerField(
        default=0, choices=DINNER_PICKUP_TIME, help_text="")

    dinner_pickupTime_end = models.IntegerField(default=len(
        DINNER_PICKUP_TIME) - 1, choices=DINNER_PICKUP_TIME, help_text="")

    class Meta:
        abstract = True


class StoreStatus(models.Model):
    status = models.IntegerField(default=0, choices=(), help_text="")

    class Meta:
        abstract = True


class Store(StoreInfo, StoreSetting, StoreStatus):
    # Metadata
    class Meta:
        ordering = ['-name']

    # Methods
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return "{id:04d} : {name}".format(id=self.id, name=self.name)
