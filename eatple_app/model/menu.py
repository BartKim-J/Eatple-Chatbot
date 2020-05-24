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


class StockTable(models.Model):
    class Meta:
        verbose_name = "재고 관리"
        verbose_name_plural = "재고 관리"

        ordering = ['-menu']

    menu = models.ForeignKey(
        'Menu',
        on_delete=models.CASCADE,
        null=True,
        verbose_name="메뉴"
    )

    company = models.ForeignKey(
        'Company',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="B2B 제휴 업체"
    )

    status = models.CharField(
        max_length=WORD_LENGTH,
        default=OC_OPEN,
        choices=OC_STATUS,
        verbose_name="메뉴 판매 여부"
    )

    pickuped_stock = models.IntegerField(
        default=0,
        verbose_name="일일 픽업 완료"
    )

    current_stock = models.IntegerField(
        default=0,
        verbose_name="일일 주문량"
    )

    max_stock = models.IntegerField(
        default=50,
        verbose_name="일일 주문 가능량"
    )

    def getCurrentStock(self):
        orderTimeSheet = OrderTimeSheet()

        currentDate = orderTimeSheet.GetCurrentDate()
        currentDateWithoutTime = orderTimeSheet.GetCurrentDateWithoutTime()

        prevLunchOrderEditTimeStart = orderTimeSheet.GetPrevLunchOrderEditTimeStart()
        nextLunchOrderEditTimeStart = orderTimeSheet.GetNextLunchOrderEditTimeStart()

        deadline = orderTimeSheet.GetInitialCountTime()

        if(currentDate <= deadline):
            expireDate = prevLunchOrderEditTimeStart
        else:
            expireDate = nextLunchOrderEditTimeStart

        availableOrders = self.menu.getCurrentStock().filter(
            Q(ordersheet__user__company=self.company))

        self.current_stock = availableOrders.count()
        self.pickuped_stock = availableOrders.filter(
            Q(status=ORDER_STATUS_PICKUP_COMPLETED)).count()
        self.save()

        # Update Total Menu Current Stock

        return availableOrders

    def getPickupedStock(self):
        return getCurrentStock().filter(Q(status=ORDER_STATUS_PICKUP_COMPLETED))

    def __str__(self):
        return '{},{},{}'.format(self.menu.name, self.company, self.max_stock)


class Tag(models.Model):
    # Metadata
    class Meta:
        verbose_name = "태그"
        verbose_name_plural = "태그"

        ordering = ['-name']

    name = models.CharField(
        max_length=WORD_LENGTH,
        unique=True,
        verbose_name="검색 태그"
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
        unique=True,
        verbose_name="픽업 시간"
    )

    def __str__(self):
        return '{} - {}'.format(self.time.strftime("%H시 %M분"), dict(SELLING_TIME_CATEGORY)[self.selling_time])


class MenuInfo(models.Model):
    store = models.ForeignKey(
        'Store',
        on_delete=models.CASCADE,
        null=True,
        verbose_name="상점"
    )

    menu_id = models.CharField(
        default='N/A',
        max_length=WORD_LENGTH,
        unique=True,
        verbose_name="메뉴 고유 번호"
    )

    name = models.CharField(
        max_length=STRING_LENGTH,
        verbose_name="메뉴명"
    )

    name_partner = models.CharField(
        max_length=STRING_LENGTH,
        null=True,
        verbose_name="점주 표기용 메뉴명"
    )

    index = models.IntegerField(
        default=0,
        verbose_name="우선순위"
    )

    class Meta:
        abstract = True


class MenuSetting(models.Model):
    type = models.CharField(
        max_length=WORD_LENGTH,
        default=STORE_TYPE_B2B_AND_NORMAL,
        choices=MENU_TYPE,
        verbose_name="유형"
    )

    description = models.TextField(
        blank=True,
        verbose_name="메뉴 설명"
    )

    tag = models.ManyToManyField(
        'Tag',
        verbose_name="검색 태그"
    )

    image = models.ImageField(
        blank=True,
        default=DEFAULT_MENU_IMAGE_PATH,
        upload_to=menu_directory_path,
        storage=OverwriteStorage(),
        verbose_name="메뉴 이미지"
    )

    soldout_image = models.ImageField(
        blank=True,
        default=DEFAULT_MENU_IMAGE_PATH,
        upload_to=menu_soldout_directory_path,
        storage=OverwriteStorage(),
        verbose_name="메뉴 이미지(매진)"
    )

    selling_time = models.CharField(
        max_length=WORD_LENGTH,
        choices=SELLING_TIME_CATEGORY,
        default=SELLING_TIME_LUNCH,
        verbose_name="판매 시간대"
    )

    pickup_time = models.ManyToManyField(
        'PickupTime',
        verbose_name="픽업 시간"
    )

    price = models.IntegerField(
        default=6000,
        verbose_name="가격(원)"
    )

    price_origin = models.IntegerField(
        default=6000,
        verbose_name="매장가격(원)"
    )

    class Meta:
        abstract = True


class MenuStatus(models.Model):

    pickuped_stock = models.IntegerField(
        default=0,
        verbose_name="일일 픽업 완료"
    )

    current_stock = models.IntegerField(
        default=0,
        verbose_name="일일 주문량"
    )

    max_stock = models.IntegerField(
        default=50,
        verbose_name="일일 주문 가능량"
    )

    status = models.CharField(
        max_length=WORD_LENGTH,
        default=OC_OPEN,
        choices=OC_STATUS,
        verbose_name="메뉴 판매 여부"
    )

    class Meta:
        abstract = True


class Menu(MenuInfo, MenuStatus, MenuSetting):
    class Meta:
        verbose_name = "메뉴 리스트"
        verbose_name_plural = "메뉴 리스트"

        ordering = ['store', 'name']

    def __init__(self, *args, **kwargs):
        super(Menu, self).__init__(*args, **kwargs)

        if (self.id == None):
            try:
                self.id = Menu.objects.latest('id').id + 1
            except (Menu.DoesNotExist) as ex:
                self.id = 1

        self.menu_id = '{id:04X}'.format(id=self.id)

    def getCurrentStock(self):
        orderTimeSheet = OrderTimeSheet()

        currentDate = orderTimeSheet.GetCurrentDate()
        currentDateWithoutTime = orderTimeSheet.GetCurrentDateWithoutTime()

        prevLunchOrderEditTimeStart = orderTimeSheet.GetPrevLunchOrderEditTimeStart()
        nextLunchOrderEditTimeStart = orderTimeSheet.GetNextLunchOrderEditTimeStart()

        deadline = orderTimeSheet.GetInitialCountTime()

        # order deadline  ~ pickup-day 16:20 , get yesterday 16:30 ~ orders
        if(currentDate <= deadline):
            expireDate = prevLunchOrderEditTimeStart
        # over deadline pickup-day 16:20 ~ , get today 16:30 ~ order
        else:
            expireDate = nextLunchOrderEditTimeStart

        availableOrders = Order.objects.filter(menu=self).filter(
            (
                Q(status=ORDER_STATUS_PICKUP_COMPLETED) |
                Q(status=ORDER_STATUS_PICKUP_WAIT) |
                Q(status=ORDER_STATUS_PICKUP_PREPARE) |
                Q(status=ORDER_STATUS_ORDER_CONFIRM_WAIT) |
                Q(status=ORDER_STATUS_ORDER_CONFIRMED)
            ) &
            Q(payment_date__gte=expireDate)
        )
        self.current_stock = availableOrders.count()
        self.pickuped_stock = availableOrders.filter(
            Q(status=ORDER_STATUS_PICKUP_COMPLETED)).count()
        self.save()

        return availableOrders

    def getPickupedStock(self):
        return getCurrentStock().filter(Q(status=ORDER_STATUS_PICKUP_COMPLETED))

    def imgURL(self):
        try:
            return self.image.url
        except Exception as ex:
            return DEFAULT_MENU_IMAGE_PATH

    def soldOutImgURL(self):
        try:
            return self.soldout_image.url
        except Exception as ex:
            return DEFAULT_MENU_IMAGE_PATH

    def __str__(self):
        return '{name}'.format(name=self.name)
