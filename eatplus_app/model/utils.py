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

#Util Funtions
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

#Models
class DefaultImage(models.Model):
    filename     = models.CharField(max_length=STRING_LENGTH, help_text="Category")
    image        = models.ImageField(blank=False, upload_to=default_directory_path, storage=OverwriteStorage())

    # Methods
    def __str__(self):
        return "{}".format(self.filename)