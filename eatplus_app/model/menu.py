'''
    Author : Ben Kim

    @NOTE
    @BUG
    @TODO
 
'''
#Django Library
from django.db import models
from django.conf import settings
from django.urls import reverse
from django.core.files.storage import FileSystemStorage
from django_mysql.models import Model
from django.core.validators import MaxValueValidator, MinValueValidator

#External Library
import os

#Define
from eatplus_app.define import EP_define

NOT_APPLICABLE              = EP_define.NOT_APPLICABLE
DEFAULT_OBJECT_ID           = EP_define.DEFAULT_OBJECT_ID

STRING_LENGTH               = EP_define.STRING_LENGTH
WORD_LENGTH                 = EP_define.WORD_LENGTH

LUNCH_PICKUP_TIME           = EP_define.LUNCH_PICKUP_TIME
DINNER_PICKUP_TIME          = EP_define.DINNER_PICKUP_TIME

SELLING_TIME_LUNCH          = EP_define.SELLING_TIME_LUNCH
SELLING_TIME_DINNER         = EP_define.SELLING_TIME_DINNER
SELLING_TIME_CATEGORY_DICT  = EP_define.SELLING_TIME_CATEGORY_DICT
SELLING_TIME_CATEGORY       = EP_define.SELLING_TIME_CATEGORY



DEFAULT_MENU_IMAGE_PATH     = "STORE_DB/images/default/menuImg.png"

#Utils
from eatplus_app.model.utils import OverwriteStorage
from eatplus_app.model.utils import menu_directory_path

#Models
class Category(models.Model):
    # Metadata
    class Meta:
        #abstract = True
        ordering  = ['-index']

    name          = models.CharField(max_length=STRING_LENGTH, help_text="Category")
    index         = models.IntegerField(default=0, help_text="Category Index")

    # Methods
    def __str__(self):
        return "{}".format(self.name)

class SubCategory(models.Model):
    # Metadata
    class Meta:
        #abstract = True
        ordering = ['-index']

    category      = models.ForeignKey(Category, on_delete=models.CASCADE)
    name          = models.CharField(max_length=STRING_LENGTH, help_text="Sub Category")
    index         = models.IntegerField(default=0, help_text="Sub Category Index")
    # Methods
    def __str__(self):
        return "{} - {}".format(self.category, self.name)



class Menu(models.Model):
    # Metadata
    class Meta:
        ordering = ['-name']


    storeInstance    = models.ForeignKey('Store', on_delete=models.CASCADE, default=DEFAULT_OBJECT_ID)
    
    # Menu Info

    sellingTime      = models.CharField(max_length=STRING_LENGTH, choices=SELLING_TIME_CATEGORY, default=SELLING_TIME_CATEGORY[SELLING_TIME_LUNCH])

    name             = models.CharField(default="Menu Name", max_length=STRING_LENGTH, help_text="Menu Name")
    description      = models.TextField(default="Description", help_text="Description")

    categories       = models.ManyToManyField(SubCategory)
    
    image            = models.ImageField(default=DEFAULT_MENU_IMAGE_PATH, blank=True, upload_to=menu_directory_path, storage=OverwriteStorage())

    price            = models.IntegerField(default=5500, help_text="Price") 
    discount         = models.IntegerField(default=0, help_text="Discount")

    current_stock    = models.IntegerField(default=0, help_text="Current Stock")

    is_status        = models.IntegerField(default=0, choices=(), help_text="")

    def imgURL(self):
            try:
                return self.image.url
            except ValueError:
                from django.contrib.staticfiles.storage import staticfiles_storage
                from django.contrib.staticfiles import finders
                
                if finders.find(self.field.static_image_path):
                    return staticfiles_storage.url(self.field.static_image_path)
                return staticfiles_storage.url(DEFAULT_MENU_IMAGE_PATH)
                
    # Methods
    def __str__(self):
        return "[{}] {} - {}".format(self.storeInstance.name, self.name, self.sellingTime)
