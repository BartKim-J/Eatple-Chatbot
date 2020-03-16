# define
from sales_app.define import *

# Eatple App Models
from eatple_app.models import PickupTime, Category, Tag
from eatple_app.system.model_type import STORE_AREA

# Django Library
from django.contrib.gis.db import models
from django.conf import settings
from django.urls import reverse
from django.core.files.storage import FileSystemStorage
from django_mysql.models import Model
from django.core.validators import MaxValueValidator, MinValueValidator


class Place(models.Model):
    class Meta:
        verbose_name = '위치'
        verbose_name_plural = '위치'

    store = models.OneToOneField(
        'Store',
        on_delete=models.CASCADE,
        unique=True,
        null=True,
        verbose_name='상점'
    )

    lat = models.DecimalField(
        default=LOCATION_DEFAULT_LAT,
        max_digits=18,
        decimal_places=14,
        verbose_name='위도'
    )

    long = models.DecimalField(
        default=LOCATION_DEFAULT_LNG,
        max_digits=18,
        decimal_places=14,
        verbose_name='경도'
    )

    point = models.PointField(
        null=True,
        blank=True,
        srid=4326,
        geography=False,
        verbose_name='위치'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if(self.store != None):
            self.point = Point(0, 0)
            super().save()

            if(self.lat <= 0 or self.long <= 0):
                self.lat = LOCATION_DEFAULT_LAT
                self.long = LOCATION_DEFAULT_LNG

            self.point = Point(y=float(self.lat), x=float(self.long))
            super().save()
        else:
            pass

    def __str__(self):
        return '{},{}'.format(round(self.lat, 6), round(self.long, 6))


class CRN(models.Model):
    class Meta:
        verbose_name = '사업자 등록번호'
        verbose_name_plural = '사업자 등록번호'

    store = models.OneToOneField(
        'Store',
        on_delete=models.CASCADE,
        unique=True,
        null=True,
        verbose_name='상점'
    )

    CRN_id = models.CharField(
        max_length=10,
        help_text='Unique ID',
        blank=True,
        null=True,
        verbose_name='사업자 등록번호'
    )

    UID = models.CharField(
        max_length=3,
        help_text='Unique ID',
        verbose_name='UID'
    )

    CC = models.CharField(
        max_length=2,
        help_text='Corporation Classification Code',
        verbose_name='CC'
    )

    SN = models.CharField(
        max_length=4,
        help_text='Serial Number',
        verbose_name='SN'
    )

    VN = models.CharField(
        max_length=1,
        help_text='Vertification Number',
        verbose_name='VN'
    )

    def __init__(self, *args, **kwargs):
        super(CRN, self).__init__(*args, **kwargs)

        self.CRN_id = '{}{}{}{}'.format(
            self.UID,
            self.CC,
            self.SN,
            self.VN
        )

        super(CRN, self).save()

    def __str__(self):
        return '{UID}-{CC}-{SN}{VN}'.format(
            UID=self.UID,
            CC=self.CC,
            SN=self.SN,
            VN=self.VN
        )


class SalesRecord(models.Model):
    class Meta:
        ordering = ['-record_date']
        verbose_name = '영업 활동 내역'
        verbose_name_plural = '영업 활동 내역'

    store = models.ForeignKey(
        'Store',
        on_delete=models.CASCADE,
        null=True,
        verbose_name='점포'
    )

    activity_memo = models.TextField(
        blank=True,
        verbose_name='영업 활동 내역'
    )

    activity_date = models.CharField(
        default=timezone.now().strftime(
            '%-m월 %-d일 %p %-I시 %-M분').replace('AM', '오전').replace('PM', '오후'),
        max_length=STRING_LENGTH,
        verbose_name='활동일'
    )

    record_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='기록일'
    )

    def save(self, *args, **kwargs):
        super().save()

    def __str__(self):
        return '{}'.format(self.record_date)


class Member(models.Model):
    class Meta:
        ordering = ['-name']
        verbose_name = '직원'
        verbose_name_plural = '직원'

    store = models.ForeignKey(
        'Store',
        on_delete=models.CASCADE,
        null=True,
        verbose_name='점포'
    )

    name = models.CharField(
        max_length=WORD_LENGTH,
        verbose_name='이름'
    )

    phone_number = PhoneNumberField(
        null=True,
        blank=True,
        verbose_name='전화번호'
    )

    level = models.CharField(
        max_length=WORD_LENGTH,
        default=MEMBER_LEVEL_NORMAL,
        choices=MEMBER_LEVEL_TYPE,
        verbose_name='직함'
    )

    def save(self, *args, **kwargs):
        super().save()

    def __str__(self):
        return '{}'.format(self.name)


class StoreBasicInfo(models.Model):
    class Meta:
        verbose_name = '세부 정보'
        verbose_name_plural = '세부 정보'

        abstract = True

    name = models.CharField(
        max_length=WORD_LENGTH,
        verbose_name='점포명'
    )

    area = models.CharField(
        max_length=WORD_LENGTH,
        default=STORE_AREA[0],
        choices=STORE_AREA,
        verbose_name='지역코드'
    )

    addr = models.CharField(
        max_length=STRING_LENGTH,
        verbose_name='점포 주소'
    )

    category = models.ManyToManyField(
        Category,
        blank=True,
        verbose_name='가게 분류',
        related_name='sales_store_category'
    )

    tag = models.ManyToManyField(
        Tag,
        blank=True,
        verbose_name='가게 세부 분류',
        related_name='sales_store_tag'
    )

    owner = models.CharField(
        max_length=WORD_LENGTH,
        verbose_name='담당자'
    )

    phone_number = PhoneNumberField(
        null=True,
        blank=True,
        verbose_name='연락처'
    )

    level = models.CharField(
        max_length=WORD_LENGTH,
        default=MEMBER_LEVEL_NORMAL,
        choices=MEMBER_LEVEL_TYPE,
        verbose_name='직급'
    )

    class Meta:
        abstract = True


class StoreDetailInfo(models.Model):
    class Meta:
        verbose_name = '가게 정보'
        verbose_name_plural = '가게 정보'

        abstract = True

    pickup_time = models.ManyToManyField(
        PickupTime,
        blank=True,
        verbose_name='픽업가능 시간',
        related_name='sales_store_pickup_time'
    )

    container_support = models.BooleanField(
        default=False,
        verbose_name='용기 사용 유무'
    )

    spoon_support = models.BooleanField(
        default=False,
        verbose_name='수저 사용 유무'
    )

    plastic_bag_support = models.BooleanField(
        default=False,
        verbose_name='비닐 사용 유무'
    )

    store_memo = models.TextField(
        blank=True,
        verbose_name='점포 관련 메모'
    )


class StoreSales(models.Model):
    class Meta:
        verbose_name = '영업 현황'
        verbose_name_plural = '영업 현황'

        abstract = True

    progress_level = models.CharField(
        max_length=WORD_LENGTH,
        default=PROGRESS_LEVEL_N,
        choices=PROGRESS_LEVEL_TYPE,
        verbose_name='진척도'
    )

    sales_memo = models.TextField(
        blank=True,
        verbose_name='영업 관련 메모'
    )


class StoreCustomer(models.Model):
    class Meta:
        verbose_name = '고객 관리'
        verbose_name_plural = '고객 관리'

        abstract = True

    customer_level = models.CharField(
        max_length=WORD_LENGTH,
        default=UP_AND_LOW_LEVEL_LOWER,
        choices=UP_AND_LOW_LEVEL_TYPE,
        verbose_name='우호도'
    )

    customer_memo = models.TextField(
        blank=True,
        verbose_name='특이사항'
    )


class Store(StoreBasicInfo, StoreDetailInfo, StoreSales, StoreCustomer):
    class Meta:
        verbose_name = '점포'
        verbose_name_plural = '점포'

        ordering = ['-name']

    def __str__(self):
        return '{name}'.format(name=self.name)
