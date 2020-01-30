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
from eatple_app.model.utils import menu_directory_path, menu_soldout_directory_path

# Models
from eatple_app.model.order import OrderSheet, Order

# Define
from eatple_app.define import *

DEFAULT_MENU_IMAGE_PATH = 'STORE_DB/images/default/menuImg.png'

class Tag(models.Model):
    # Metadata
    class Meta:
        verbose_name = "태그"
        verbose_name_plural = "태그"
        
        ordering = ['-name']

    name = models.CharField(
        max_length=WORD_LENGTH, 
        verbose_name = "검색 태그"
    )

    def __str__(self):
        return '{}'.format(self.name)

class PickupTime(models.Model):
    class Meta:
        verbose_name = "픽업 시간"
        verbose_name_plural = "픽업 시간"
        
        ordering = ['time']

    selling_time = models.CharField(
        max_length=WORD_LENGTH,
        choices=SELLING_TIME_CATEGORY,
        default=SELLING_TIME_LUNCH,
        help_text='판매 시간*'
    )

    time = models.TimeField(
        default=timezone.now,
        verbose_name="픽업 시간"
    )
    
    def __str__(self):
        return '{} - {}'.format(self.time.strftime("%H시 %M분"), dict(SELLING_TIME_CATEGORY)[self.selling_time])
        
class MenuInfo(models.Model):
    store = models.ForeignKey(
        'Store', 
        on_delete=models.CASCADE, 
        null=True,
        verbose_name = "상점"
    )

    menu_id = models.CharField(
        default='N/A',
        max_length=WORD_LENGTH, 
        unique=True,
        verbose_name = "메뉴 고유 번호"
    )

    name = models.CharField(
        max_length=STRING_LENGTH, 
        verbose_name = "메뉴명"
    )

    class Meta:
        abstract = True


class MenuSetting(models.Model):
    description = models.TextField(
        blank=True,
        verbose_name = "메뉴 설명"
    )

    tag = models.ManyToManyField(
        'Tag',
        verbose_name = "검색 태그"
    )

    image = models.ImageField(
        default=DEFAULT_MENU_IMAGE_PATH,
        upload_to=menu_directory_path, 
        storage=OverwriteStorage(),
        verbose_name = "메뉴 이미지"
    )

    soldout_image = models.ImageField(
        default=DEFAULT_MENU_IMAGE_PATH,
        upload_to=menu_soldout_directory_path, 
        storage=OverwriteStorage(),
        verbose_name = "메뉴 이미지(매진)"
    )

    selling_time = models.CharField(
        max_length=WORD_LENGTH,
        choices=SELLING_TIME_CATEGORY,
        default=SELLING_TIME_LUNCH,
        verbose_name = "판매 시간대"
    )


    pickup_time = models.ManyToManyField(
        'PickupTime',
        verbose_name = "픽업 시간"
    )

    price = models.IntegerField(
        default=6000, 
        verbose_name = "가격"
    )
    
    discount = models.IntegerField(
        default=0, 
        verbose_name = "할인율"
    )

    class Meta:
        abstract = True


class MenuStatus(models.Model):
    current_stock = models.IntegerField(
        default=0, 
        verbose_name = "현재 재고"
    )
    
    max_stock = models.IntegerField(
        default=50, 
        verbose_name = "일일 재고"
    )

    status = models.CharField(
        max_length=WORD_LENGTH, 
        default=OC_OPEN, 
        choices=OC_STATUS, 
        verbose_name = "메뉴 판매 여부"
    )

    class Meta:
        abstract = True


class Menu(MenuInfo, MenuStatus, MenuSetting):
    # Metadata
    class Meta:
        ordering = ['status','menu_id']

    def __init__(self, *args, **kwargs):
        super(Menu, self).__init__(*args, **kwargs)
        
        if (self.id == None):
            try:
                self.id = Menu.objects.latest('id').id + 1
            except (Menu.DoesNotExist) as ex:
                self.id = 1

        self.menu_id = '{id:04X}'.format(id=self.id)

    def getCurrentStock(self):
        currentDate = dateNowByTimeZone()
        expireDate = currentDate + datetime.timedelta(hours=-24)
        deadline = currentDate.replace(hour=16, minute=20, second=0)

        if(deadline >= currentDate):
            availableOrders = Order.objects.filter(menu=self).filter(
                (
                    Q(status=ORDER_STATUS_PICKUP_WAIT) |
                    Q(status=ORDER_STATUS_PICKUP_PREPARE) |
                    Q(status=ORDER_STATUS_ORDER_CONFIRM_WAIT) |
                    Q(status=ORDER_STATUS_ORDER_CONFIRMED) |
                    Q(status=ORDER_STATUS_PICKUP_COMPLETED)
                ) &
                Q(payment_date__gt=expireDate)
            )
        else:
            availableOrders = Order.objects.none()

        print(availableOrders)
        self.current_stock = availableOrders.count()
        self.save()
        
        return availableOrders


    def imgURL(self):
        try:
            return self.image.url
        except ValueError:
            return DEFAULT_MENU_IMAGE_PATH
        
    def soldOutImgURL(self):
        try:
            return self.soldout_image.url
        except ValueError:
            return DEFAULT_MENU_IMAGE_PATH
        
    def __str__(self):
        return '{name}'.format(name=self.name)
