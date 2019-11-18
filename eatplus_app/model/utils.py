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

DEFAULT_IMAGE_PATH     = "STORE_DB/images/default/defaultImg.png"

#Util Funtions
class OverwriteStorage(FileSystemStorage):
    def get_available_name(self, name, max_length=None):
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

#Models
class DefaultImage(models.Model):
    # Metadata
    class Meta:
        ordering = ['-name']
    
    name         = models.CharField(default="", max_length=STRING_LENGTH, help_text="subject name")
    
    filename     = models.CharField(max_length=STRING_LENGTH, help_text="filename")
    image        = models.ImageField(blank=False, upload_to=default_directory_path, storage=OverwriteStorage())

    # Methodssadfasdfas
    def __str__(self):
        return "{}".format(self.name)
    
    
class UserManual(models.Model):
    class Meta:
        ordering = ['-index']
    
    index        = models.IntegerField(default=0)
    name         = models.CharField(default="", max_length=STRING_LENGTH, help_text="subject name")
    
    filename     = models.CharField(default="", max_length=STRING_LENGTH, help_text="filename")
    image        = models.ImageField(blank=False, upload_to=default_directory_path, storage=OverwriteStorage())
    
    title        = models.CharField(default="", max_length=STRING_LENGTH, help_text="Title", blank=True)
    description  = models.TextField(default="", help_text="Description", blank=True)

    def imgURL(self):
        try:
            return self.image.url
        except ValueError:
            return DEFAULT_IMAGE_PATH

    # Methods
    def __str__(self):
        return "{}".format(self.name)
    
class UserIntro(models.Model):
    class Meta:
        ordering = ['-index']
    
    index        = models.IntegerField(default=0)
    name         = models.CharField(default="", max_length=STRING_LENGTH, help_text="subject name")
    
    filename     = models.CharField(default="", max_length=STRING_LENGTH, help_text="filename")
    image        = models.ImageField(blank=False, upload_to=default_directory_path, storage=OverwriteStorage())
    
    title        = models.CharField(default="", max_length=STRING_LENGTH, help_text="Title", blank=True)
    description  = models.TextField(default="", help_text="Description", blank=True)

    def imgURL(self):
        try:
            return self.image.url
        except ValueError:
            return DEFAULT_IMAGE_PATH

    # Methods
    def __str__(self):
        return "{}".format(self.name)

class PartnerIntro(models.Model):
    class Meta:
        ordering = ['-index']
    
    index        = models.IntegerField(default=0)
    name         = models.CharField(default="", max_length=STRING_LENGTH, help_text="subject name")
    
    filename     = models.CharField(default="", max_length=STRING_LENGTH, help_text="filename")
    image        = models.ImageField(blank=False, upload_to=default_directory_path, storage=OverwriteStorage())
    
    title        = models.CharField(default="", max_length=STRING_LENGTH, help_text="Title", blank=True)
    description  = models.TextField(default="", help_text="Description", blank=True)

    def imgURL(self):
        try:
            return self.image.url
        except ValueError:
            return DEFAULT_IMAGE_PATH

    # Methods
    def __str__(self):
        return "{}".format(self.name)
class PartnerManual(models.Model):
    class Meta:
        ordering = ['-name']
    
    index        = models.IntegerField(default=0)
    name         = models.CharField(default="", max_length=STRING_LENGTH, help_text="subject name")
    
    filename     = models.CharField(default="", max_length=STRING_LENGTH, help_text="filename")
    image        = models.ImageField(blank=False, upload_to=default_directory_path, storage=OverwriteStorage())
    
    title        = models.CharField(default="", max_length=STRING_LENGTH, help_text="Title", blank=True)
    description  = models.TextField(default="", help_text="Description", blank=True)

    def imgURL(self):
        try:
            return self.image.url
        except ValueError:
            return DEFAULT_IMAGE_PATH

    # Methods
    def __str__(self):
        return "{}".format(self.name)