# Django Library
from django.db import models
from django.conf import settings
from django.urls import reverse
from django.core.files.storage import FileSystemStorage
from django_mysql.models import Model
from django.core.validators import MaxValueValidator, MinValueValidator
from django import forms

# System Library
import os
from random import *

# Utils
from eatple_app.model.utils import OverwriteStorage
from eatple_app.model.utils import logo_directory_path

# define
from eatple_app.define import *


class CRN(models.Model):
    store = models.OneToOneField(
        'Store', on_delete=models.CASCADE, unique=True, null=True)

    UID = models.CharField(max_length=3, help_text="Unique ID")

    CC = models.CharField(
        max_length=2, help_text="Corporation Classification Code")

    SN = models.CharField(max_length=4, help_text="Serial Number")

    VN = models.CharField(max_length=1, help_text="Vertification Number")

    def __str__(self):
        return "{UID}-{CC}-{SN}{VN}".format(UID=self.UID, CC=self.CC, SN=self.SN, VN=self.VN)


class PickupTime(models.Model):
    class Meta:
        ordering = ['time']

    store = models.ForeignKey('Store', on_delete=models.CASCADE, null=True)

    time = models.TimeField(default=timezone.now)
    
    status = models.IntegerField(
        default=OC_OPEN,
        choices=OC_STATUS
    )


class StoreInfo(models.Model):
    store_id = models.CharField(default="N/A",
                                max_length=STRING_LENGTH, help_text="Store ID",
                                unique=True)

    name = models.CharField(max_length=STRING_LENGTH, help_text="Store Name")

    addr = models.CharField(max_length=STRING_LENGTH,
                            help_text="Store Address")

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
    status = models.IntegerField(
        default=OC_OPEN,
        choices=OC_STATUS
    )

    class Meta:
        abstract = True


class Store(StoreInfo, StoreSetting, StoreStatus):
    class Meta:
        ordering = ['-name']

    def __init__(self, *args, **kwargs):
        super(Store, self).__init__(*args, **kwargs)

        if (self.id == None):
            try:
                self.id = Store.objects.latest('id').id + 1
            except (Store.DoesNotExist) as ex:
                self.id = 1

        self.store_id = "{area:04X}-{id:04X}".format(area=0, id=self.id)

    def save(self, *args, **kwargs):
        super().save()

    def __str__(self):
        return "{name}".format(name=self.name)
