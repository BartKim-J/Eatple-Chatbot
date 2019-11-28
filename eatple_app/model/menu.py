# Django Library
from eatple_app.model.utils import menu_directory_path
from eatple_app.model.utils import OverwriteStorage
from django.db import models
from django.conf import settings
from django.urls import reverse
from django.core.files.storage import FileSystemStorage
from django_mysql.models import Model
from django.core.validators import MaxValueValidator, MinValueValidator

# External Library
import os

# Define
from eatple_app.define import EP_define

NOT_APPLICABLE = EP_define.NOT_APPLICABLE
DEFAULT_OBJECT_ID = EP_define.DEFAULT_OBJECT_ID

STRING_LENGTH = EP_define.STRING_LENGTH
WORD_LENGTH = EP_define.WORD_LENGTH

LUNCH_PICKUP_TIME = EP_define.LUNCH_PICKUP_TIME
DINNER_PICKUP_TIME = EP_define.DINNER_PICKUP_TIME

SELLING_TIME_LUNCH = EP_define.SELLING_TIME_LUNCH
SELLING_TIME_DINNER = EP_define.SELLING_TIME_DINNER
SELLING_TIME_CATEGORY_DICT = EP_define.SELLING_TIME_CATEGORY_DICT
SELLING_TIME_CATEGORY = EP_define.SELLING_TIME_CATEGORY

DEFAULT_MENU_IMAGE_PATH = "STORE_DB/images/default/menuImg.png"


class Category(models.Model):
    # Metadata
    class Meta:
        # abstract = True
        ordering = ['-index']

    name = models.CharField(max_length=STRING_LENGTH, help_text="Category")
    index = models.IntegerField(default=0, help_text="Category Index")

    # Methods
    def __str__(self):
        return "{}".format(self.name)


class Tag(models.Model):
    # Metadata
    class Meta:
        # abstract = True
        ordering = ['-name']

    name = models.CharField(max_length=STRING_LENGTH, help_text="Tag")

    # Methods

    def __str__(self):
        return "{}".format(self.name)


class MenuInfo(models.Model):
    store = models.ForeignKey(
        'Store', on_delete=models.CASCADE, null=True)

    menu_id = models.CharField(default="N/A",
                               max_length=STRING_LENGTH, help_text="Menu ID",
                               unique=True)

    name = models.CharField(max_length=STRING_LENGTH, help_text="Menu Name")

    class Meta:
        abstract = True


class MenuSetting(models.Model):
    description = models.TextField(help_text="Description", blank=True)

    tag = models.ManyToManyField(Tag)

    image = models.ImageField(
        blank=True, upload_to=menu_directory_path, storage=OverwriteStorage())

    sellingTime = models.CharField(
        max_length=STRING_LENGTH, choices=SELLING_TIME_CATEGORY, default=SELLING_TIME_CATEGORY[SELLING_TIME_LUNCH])

    price = models.IntegerField(default=6000, help_text="Price")
    discount = models.IntegerField(default=0, help_text="Discount")

    class Meta:
        abstract = True


class MenuStatus(models.Model):
    current_stock = models.IntegerField(default=0, help_text="Current Stock")
    max_stock = models.IntegerField(default=50, help_text="Max Stock")

    status = models.IntegerField(default=0, choices=(), help_text="")

    class Meta:
        abstract = True


class Menu(MenuInfo, MenuStatus, MenuSetting):
    # Metadata
    class Meta:
        ordering = ['-menu_id']

    def __init__(self, *args, **kwargs):
        super(Menu, self).__init__(*args, **kwargs)

        if (self.id == None):
            try:
                self.id = Menu.objects.latest('id').id + 1
            except (Menu.DoesNotExist) as ex:
                self.id = 1

        self.menu_id = "{id:04x}".format(id=self.id)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def imgURL(self):
        try:
            return self.image.url
        except ValueError:
            return DEFAULT_MENU_IMAGE_PATH

    def __str__(self):
        return "{sellingTime}메뉴 - {name}".format(name=self.name, sellingTime=self.sellingTime)
