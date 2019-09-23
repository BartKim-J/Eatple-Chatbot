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

#Models 
from eatplus_app.define import EP_define

#GLOBAL CONFIG
NOT_APPLICABLE              = EP_define.NOT_APPLICABLE
DEFAULT_OBJECT_ID           = EP_define.DEFAULT_OBJECT_ID

STRING_LENGTH               = EP_define.STRING_LENGTH
WORD_LENGTH                 = EP_define.WORD_LENGTH

LUNCH_PICKUP_TIME           = EP_define.LUNCH_PICKUP_TIME
DINNER_PICKUP_TIME          = EP_define.DINNER_PICKUP_TIME

MANAGEMENT_CODE_LENGTH      = EP_define.MANAGEMENT_CODE_LENGTH

SELLING_TIME_LUNCH          = EP_define.SELLING_TIME_LUNCH
SELLING_TIME_DINNER         = EP_define.SELLING_TIME_DINNER
SELLING_TIME_CATEGORY_DICT  = EP_define.SELLING_TIME_CATEGORY_DICT
SELLING_TIME_CATEGORY       = EP_define.SELLING_TIME_CATEGORY

#STATIC CONFIG
class OverwriteStorage(FileSystemStorage):
    def get_available_name(self, name, max_length=None):
        print(self)
        print("HISIDFJAISF")
        # If the filename already exists, remove it as if it was a true file system
        if self.exists(name):
            print(os.path.join(settings.MEDIA_ROOT, name))
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return name
        
def set_filename_format(instance, filename, toFilename):
    return "{filename}{extension}".format(
        filename=toFilename,
        extension=".png",
    )


def menu_directory_path(instance, filename):
    path = "STORE_DB/images/{storename}/{menuname}/{filename}".format(
        storename=instance.storeInstance.name,
        menuname=instance.name,
        filename=set_filename_format(instance, filename, "menuImg"),
    )

    return path

def logo_directory_path(instance, filename):
    path = "STORE_DB/images/{storename}/{filename}".format(
        storename=instance.storeInstance.name,
        menuname=instance.name,
        filename=set_filename_format(instance, filename, "logoImg"),
    )

    return path

def default_directory_path(instance, filename):
    path = "STORE_DB/images/default/{filename}".format(
        filename=set_filename_format(instance, filename, instance.filename),
    )

    return path

class DefaultImage(models.Model):
    filename     = models.CharField(max_length=STRING_LENGTH, help_text="Category")
    image        = models.ImageField(blank=False, upload_to=default_directory_path, storage=OverwriteStorage())

    # Methods
    def __str__(self):
        return "{}".format(self.filename)

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

class Store(models.Model):
    # Metadata
    class Meta: 
        ordering = ['-name']

    # Store Info
    name         = models.CharField(default="Store Name", max_length=STRING_LENGTH,
                                    help_text="Store Name")
    addr         = models.CharField(default="Address", max_length=STRING_LENGTH, 
                                    help_text="Address") 
    owner        = models.CharField(default="Owner", max_length=WORD_LENGTH, 
                                    help_text="Owner")
    description  = models.TextField(default="Store Dscription",
                                    help_text="Store Dscription")

    logo         = models.ImageField(default="STORE_DB/images/default/logoImg.png", upload_to=logo_directory_path, storage=OverwriteStorage())

    lunch_pickupTime_start  = models.IntegerField(default=0, choices=LUNCH_PICKUP_TIME, help_text="")
    lunch_pickupTime_end    = models.IntegerField(default=len(LUNCH_PICKUP_TIME) - 1, choices=LUNCH_PICKUP_TIME, help_text="")

    dinner_pickupTime_start = models.IntegerField(default=0, choices=DINNER_PICKUP_TIME, help_text="")
    dinner_pickupTime_end   = models.IntegerField(default=len(DINNER_PICKUP_TIME) - 1, choices=DINNER_PICKUP_TIME, help_text="")


    # Methods
    def __str__(self):
        return "{}".format(self.name)

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
    
    image            = models.ImageField(default="STORE_DB/images/default/menuImg.png", upload_to=menu_directory_path, storage=OverwriteStorage())

    price            = models.IntegerField(default=5500, help_text="Price") 
    discount         = models.IntegerField(default=0, help_text="Discount")


    sales_count      = models.IntegerField(default=0, help_text="Total Sales Count")
    current_stock    = models.IntegerField(default=0, help_text="Current Stock")


    management_code  = models.CharField(max_length=MANAGEMENT_CODE_LENGTH, blank=True, null=True,
                                        help_text="Menu Magement Code")
    is_status        = models.IntegerField(default=0, choices=(), help_text="")

    # Methods
    def __str__(self):
        return "[{}] {} - {}".format(self.storeInstance.name, self.name, self.sellingTime)
