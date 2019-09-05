#Django Library
from django.urls import reverse
from django.db import models
from django_mysql.models import Model

#External Library
import datetime

#Models 
from .models_config import Config

#GLOBAL CONFIG
NOT_APPLICABLE          = Config.NOT_APPLICABLE
DEFAULT_OBJECT_ID       = Config.DEFAULT_OBJECT_ID

STRING_LENGTH           = Config.STRING_LENGTH
WORD_LENGTH             = Config.WORD_LENGTH

MANAGEMENT_CODE_LENGTH  = Config.MANAGEMENT_CODE_LENGTH

MENU_LUNCH              = Config.MENU_LUNCH
MENU_CATEGORY           = Config.MENU_CATEGORY

#STATIC CONFIG

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

    menus        = models.ManyToManyField('Menu')

    logo         = models.ImageField(blank=True, upload_to="eatplus_chatot_app/DB/logo_img")

    # Methods
    def __str__(self):
        return "{}".format(self.name)

class Menu(models.Model):
    # Metadata
    class Meta:
        ordering = ['-name']


    storeInstance         = models.ForeignKey('Store', on_delete=models.CASCADE, default=DEFAULT_OBJECT_ID)
    
    # Menu Info
    management_code  = models.CharField(max_length=MANAGEMENT_CODE_LENGTH, blank=True, null=True,
                                        help_text="Menu Magement Code")
    name             = models.CharField(default="Menu Name", max_length=STRING_LENGTH, 
                                        help_text="Menu Name")

    sellingTime      = models.CharField(max_length=STRING_LENGTH, choices=MENU_CATEGORY, default=MENU_CATEGORY[MENU_LUNCH])
    categories       = models.ManyToManyField(Category)
    sub_categories   = models.ManyToManyField(SubCategory)

    price            = models.IntegerField(default=5500, 
                                           help_text="Price") 
    discount         = models.IntegerField(default=0,
                                           help_text="Discount")
    description      = models.TextField(default="Description", 
                                        help_text="Description")


    sales_count      = models.IntegerField(default=0,
                                           help_text="Total Sales Count")
    current_stock    = models.IntegerField(default=0,
                                           help_text="Current Stock")                                           
    logistics_code   = models.CharField(max_length=MANAGEMENT_CODE_LENGTH, blank=True, null=True,
                                        help_text="Menu Logistics Code")

    is_status        = models.IntegerField(default=0, choices=(

    ), help_text="")

    # Methods
    def __str__(self):
        return "[{}] {} - {}".format(self.storeInstance.name, self.name, self.sellingTime)
