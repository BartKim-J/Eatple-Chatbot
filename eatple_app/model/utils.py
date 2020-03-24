
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

DEFAULT_IMAGE_PATH = 'STORE_DB/images/default/defaultImg.png'


class OverwriteStorage(FileSystemStorage):
    def get_available_name(self, name, max_length=None):
        # If the filename already exists, remove it as if it was a true file system
        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return name


def set_filename_format(instance, filename, toFilename):
    return '{filename}{extension}'.format(
        filename=toFilename,
        extension='.png',
    )


def menu_directory_path(instance, filename):
    path = 'STORE_DB/images/{storename}/{menuname}/{number}{filename}'.format(
        storename=instance.store.name,
        menuname=instance.name,
        filename=set_filename_format(instance, filename, 'menuImg'),
        number=dateNowByTimeZone().strftime("%f"),
    )

    return path


def menu_soldout_directory_path(instance, filename):
    path = 'STORE_DB/images/{storename}/{menuname}/{number}{filename}'.format(
        storename=instance.store.name,
        menuname=instance.name,
        filename=set_filename_format(instance, filename, 'menuSoldOutImg'),
        number=dateNowByTimeZone().strftime("%f"),
    )

    return path


def logo_directory_path(instance, filename):
    path = 'STORE_DB/images/{storename}/{number}{filename}'.format(
        storename=instance.name,
        filename=set_filename_format(instance, filename, 'logoImg'),
        number=dateNowByTimeZone().strftime('%f'),
    )

    return path


def store_directory_path(instance, filename):
    path = 'STORE_DB/images/{storename}/{number}{filename}'.format(
        storename=instance.name,
        filename=set_filename_format(instance, filename, ''),
        number=dateNowByTimeZone().strftime('%f'),
    )

    return path


def b2b_logo_directory_path(instance, filename):
    path = 'B2B_DB/images/{b2b_name}/{number}{filename}'.format(
        b2b_name=instance.name,
        filename=set_filename_format(instance, filename, 'logoImg'),
        number=dateNowByTimeZone().strftime('%f'),
    )

    return path


def default_directory_path(instance, filename):
    path = 'STORE_DB/images/default/{filename}'.format(
        filename=set_filename_format(instance, filename, instance.filename),
    )

    return path


class DefaultImage(models.Model):
    # Metadata
    class Meta:
        verbose_name = "디폴트 이미지"
        verbose_name_plural = "디폴트 이미지"

        ordering = ['-name']

    name = models.CharField(
        default='',
        max_length=WORD_LENGTH,
        help_text='subject name'
    )

    filename = models.CharField(
        max_length=WORD_LENGTH,
        help_text='filename'
    )

    image = models.ImageField(
        blank=False,
        upload_to=default_directory_path,
        storage=OverwriteStorage()
    )

    # Methodssadfasdfas
    def __str__(self):
        return '{}'.format(self.name)
