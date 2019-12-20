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

# Utils
from eatple_app.model.utils import OverwriteStorage
from eatple_app.model.utils import menu_directory_path


# Define
from eatple_app.define import *

DEFAULT_MENU_IMAGE_PATH = 'STORE_DB/images/default/menuImg.png'

class Tag(models.Model):
    # Metadata
    class Meta:
        # abstract = True
        ordering = ['-name']

    name = models.CharField(
        max_length=WORD_LENGTH, 
        help_text='검색 태그*'
    )

    def __str__(self):
        return '{}'.format(self.name)

class PickupTime(models.Model):
    class Meta:
        ordering = ['time']

    selling_time = models.CharField(
        max_length=WORD_LENGTH,
        choices=SELLING_TIME_CATEGORY,
        default=SELLING_TIME_LUNCH,
        help_text='판매 시간*'
    )

    time = models.TimeField(default=timezone.now)
    
    def __str__(self):
        return '{} - {}'.format(self.time.strftime("%H시 %M분"), dict(SELLING_TIME_CATEGORY)[self.selling_time])
        
class MenuInfo(models.Model):
    store = models.ForeignKey(
        'Store', on_delete=models.CASCADE, null=True)

    menu_id = models.CharField(
        default='N/A',
        max_length=WORD_LENGTH, 
        unique=True,
        help_text='메뉴 고유 번호',
        )

    name = models.CharField(max_length=WORD_LENGTH, help_text='Menu Name')

    class Meta:
        abstract = True


class MenuSetting(models.Model):
    description = models.TextField(help_text='Description', blank=True)

    tag = models.ManyToManyField('Tag')

    image = models.ImageField(
        default=DEFAULT_MENU_IMAGE_PATH,
        upload_to=menu_directory_path, 
        storage=OverwriteStorage(),
        help_text='메뉴 이미지*'
    )

    selling_time = models.CharField(
        max_length=WORD_LENGTH,
        choices=SELLING_TIME_CATEGORY,
        default=SELLING_TIME_LUNCH,
        help_text='판매 시간*'
    )


    pickup_time = models.ManyToManyField(
        'PickupTime'
    )

    price = models.IntegerField(
        default=6000, 
        help_text='가격*'
    )
    
    discount = models.IntegerField(
        default=0, 
        help_text='가게 할인*'
    )

    class Meta:
        abstract = True


class MenuStatus(models.Model):
    current_stock = models.IntegerField(
        default=0, 
        help_text='재고*'
    )
    
    max_stock = models.IntegerField(
        default=50, 
        help_text='일일 재고*'
    )

    status = models.CharField(
        max_length=WORD_LENGTH, 
        default=OC_OPEN, 
        choices=OC_STATUS, 
        help_text='메뉴 판매여부*'
    )

    class Meta:
        abstract = True


class Menu(MenuInfo, MenuStatus, MenuSetting):
    # Metadata
    class Meta:
        ordering = ['menu_id']

    def __init__(self, *args, **kwargs):
        super(Menu, self).__init__(*args, **kwargs)
        
        if (self.id == None):
            try:
                self.id = Menu.objects.latest('id').id + 1
            except (Menu.DoesNotExist) as ex:
                self.id = 1

        self.menu_id = '{id:04X}'.format(id=self.id)

    def imgURL(self):
        try:
            return self.image.url
        except ValueError:
            return DEFAULT_MENU_IMAGE_PATH

    def __str__(self):
        return '{store} - {name}'.format(store=self.store.name, name=self.name)
