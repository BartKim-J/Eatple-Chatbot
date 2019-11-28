
from django.db import models
from django.conf import settings
from django.urls import reverse
from django.core.files.storage import FileSystemStorage
from django_mysql.models import Model
from django.core.validators import MaxValueValidator, MinValueValidator
from django import forms

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


class CRN(models.Model):    
    store_instance = models.OneToOneField('Store', on_delete=models.CASCADE, unique=True, null=True)

    UID = models.CharField(max_length=3, help_text="Unique ID")

    CC = models.CharField(max_length=2, help_text="Corporation Classification Code")

    SN = models.CharField(max_length=4, help_text="Serial Number")

    VN = models.CharField(max_length=1, help_text="Vertification Number")

    def __str__(self):
        return "{UID}-{CC}-{SN}{VN}".format(UID=self.UID, CC=self.CC, SN=self.SN, VN=self.VN)


class StoreInfo(models.Model):
    store_id = models.CharField(default="N/A",
                                max_length=STRING_LENGTH, help_text="Store ID",
                                unique=True)

    name = models.CharField(max_length=STRING_LENGTH, help_text="Store Name")

    addr = models.CharField(max_length=STRING_LENGTH, help_text="Store Address")

    owner = models.CharField(max_length=WORD_LENGTH, help_text="Owner")

    class Meta:
        abstract = True


class StoreSetting(models.Model):

    description = models.TextField(help_text="Store Dscription", blank=True)

    logo = models.ImageField(default="STORE_DB/images/default/logoImg.png",
                             blank=True, upload_to=logo_directory_path, storage=OverwriteStorage())

    class Meta:
        abstract = True


class StoreStatus(models.Model):
    STATUS_CHOICES = (
        ('o', 'Open'),
        ('c', 'Close'),
    )

    status = models.CharField(max_length=1, default='o', choices=STATUS_CHOICES, help_text="")
    
    class Meta:
        abstract = True


class Store(StoreInfo, StoreSetting, StoreStatus):
    # Metadata
    class Meta:
        ordering = ['-name']

    def __init__(self, *args, **kwargs):
        super(Store, self).__init__(*args, **kwargs)

        if (self.id == None):
            try:
                self.id = Store.objects.latest('id').id + 1
            except (Store.DoesNotExist) as ex:
                self.id = 1

        self.store_id = "{area:04x}-{id:04x}".format(area=0, id=self.id)

    # Methods
    def save(self, *args, **kwargs):

        super().save(*args, **kwargs)

    def __str__(self):
        return "{name}".format(name=self.name)
