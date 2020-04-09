# define
from eatple_app.define import *
# Django Library
from django.contrib.gis.db import models
from django.conf import settings
from django.urls import reverse
from django.core.files.storage import FileSystemStorage
from django_mysql.models import Model
from django.core.validators import MaxValueValidator, MinValueValidator

from sales_app.system.model_type import UP_AND_LOW_LEVEL_LOWER, UP_AND_LOW_LEVEL_TYPE

# Utils
from eatple_app.model.utils import OverwriteStorage
from eatple_app.model.utils import logo_directory_path, cover_directory_path, store_directory_path

# Coustom Model Type
from eatple_app.system.model_type_bank import *

# Models
from eatple_app.model.menu import Menu
from eatple_app.model.order import Order

DEFAULT_LOGO_IMAGE_PATH = 'STORE_DB/images/default/logo.png'
DEFAULT_FILE_PATH = 'STORE_DB/images/'


class Category(models.Model):
    # Metadata
    class Meta:
        # abstract = True
        verbose_name = '분류'
        verbose_name_plural = '분류'

        ordering = ['-name']

    name = models.CharField(
        max_length=WORD_LENGTH,
        verbose_name='분류'
    )

    # Methods
    def __str__(self):
        return '{}'.format(self.name)


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
        verbose_name='매장'
    )

    activity_memo = models.TextField(
        blank=True,
        verbose_name='영업 활동 내역'
    )

    activity_date = models.CharField(
        default=dateNowByTimeZone().strftime(
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
        return '{}'.format(self.activity_date)


class StoreInfo(models.Model):
    store_id = models.CharField(
        default='N/A',
        max_length=WORD_LENGTH,
        unique=True,
        verbose_name='상점 고유 번호'
    )

    name = models.CharField(
        max_length=WORD_LENGTH,
        verbose_name='상호'
    )

    addr = models.CharField(
        max_length=STRING_LENGTH,
        verbose_name='주소'
    )

    phone_number = PhoneNumberField(
        null=True,
        blank=True,
        verbose_name='관리자 전화번호'
    )

    owner = models.CharField(
        default='',
        max_length=WORD_LENGTH,
        verbose_name='점주명'
    )

    class Meta:
        abstract = True


class StoreSetting(models.Model):
    class Meta:
        verbose_name = '설정'
        verbose_name_plural = '설정'

        abstract = True

    category = models.ManyToManyField(
        'Category',
        verbose_name='가게 분류'
    )

    description = models.TextField(
        blank=True,
        verbose_name='가게 설명'
    )

    logo = models.ImageField(
        default=DEFAULT_LOGO_IMAGE_PATH,
        blank=True,
        upload_to=logo_directory_path,
        storage=OverwriteStorage(),
        verbose_name='로고 이미지'
    )

    cover = models.ImageField(
        default=DEFAULT_LOGO_IMAGE_PATH,
        blank=True,
        upload_to=cover_directory_path,
        storage=OverwriteStorage(),
        verbose_name='커버 이미지'
    )


class StoreStatus(models.Model):
    class Meta:
        verbose_name = '상태'
        verbose_name_plural = '상태'

        abstract = True

    status = models.CharField(
        max_length=WORD_LENGTH,
        default=STORE_OC_OPEN,
        choices=STORE_OC_STATUS,
        verbose_name='상태'
    )

    type = models.CharField(
        max_length=WORD_LENGTH,
        default=STORE_TYPE_NORMAL,
        choices=STORE_TYPE,
        verbose_name='유형'
    )

    area = models.CharField(
        max_length=WORD_LENGTH,
        default=STORE_AREA_A_3,
        choices=STORE_AREA,
        verbose_name='지역코드'
    )


class StoreSalesInfo(models.Model):
    class Meta:
        verbose_name = '영업 관리'
        verbose_name_plural = '영업 관리'

        abstract = True

    customer_level = models.CharField(
        max_length=WORD_LENGTH,
        default=UP_AND_LOW_LEVEL_LOWER,
        choices=UP_AND_LOW_LEVEL_TYPE,
        verbose_name='우호도'
    )

    sales_memo = models.TextField(
        blank=True,
        verbose_name='특이사항'
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


class StoreBankAccount(models.Model):
    class Meta:
        verbose_name = '계좌 정보'
        verbose_name_plural = '계좌 정보'

        abstract = True

    bank_email = models.EmailField(
        default='',
        blank=True,
        max_length=STRING_LENGTH,
        verbose_name='세금 계산서 이메일'
    )

    bank_type = models.CharField(
        max_length=WORD_LENGTH,
        default='100',
        choices=BANK_CODE,
        verbose_name='은행코드'
    )

    bank_owner = models.CharField(
        default='',
        blank=True,
        max_length=WORD_LENGTH,
        verbose_name='예금주명'
    )

    bank_account = models.CharField(
        default='',
        blank=True,
        max_length=WORD_LENGTH,
        verbose_name='계좌번호'
    )

    # Business registration certificate
    brc_document_file = models.ImageField(
        default=DEFAULT_FILE_PATH,
        blank=True,
        upload_to=store_directory_path,
        storage=OverwriteStorage(),
        verbose_name='사업자등록증'
    )

    # Health certificate
    hc_document_file = models.ImageField(
        default=DEFAULT_FILE_PATH,
        blank=True,
        upload_to=store_directory_path,
        storage=OverwriteStorage(),
        verbose_name='영업신고증'
    )


class Store(StoreInfo, StoreSetting, StoreStatus, StoreSalesInfo, StoreBankAccount):
    class Meta:
        verbose_name = '제휴 매장'
        verbose_name_plural = '제휴 매장'

        ordering = ['-name']

    def __init__(self, *args, **kwargs):
        super(Store, self).__init__(*args, **kwargs)

        if (self.id == None):
            try:
                self.id = Store.objects.latest('id').id + 1
            except (Store.DoesNotExist) as ex:
                self.id = 1

        self.store_id = '{area:04X}-{id:04X}'.format(area=0, id=self.id)

    def logoImgURL(self):
        try:
            return self.logo.url
        except ValueError:
            return DEFAULT_LOGO_IMAGE_PATH

    def coverImgURL(self):
        try:
            return self.cover.url
        except ValueError:
            return DEFAULT_LOGO_IMAGE_PATH

    def getCurrentStock(self):
        currentStock = 0
        menuList = Menu.objects.filter(store=self)

        for menu in menuList:
            currentStock += menu.getCurrentStock().count()

        return currentStock

    def getMontlyStock(self, before=0):
        orderTimeSheet = OrderTimeSheet()

        origin_date = orderTimeSheet.GetCurrentDate()

        target_year = origin_date.year
        target_month = (origin_date.month - before)

        if(target_month < 0):
            target_year -= 1
            target_month += 12

        range_start = origin_date.replace(
            year=target_year, month=target_month, day=1, hour=0, minute=0, second=0)

        range_end = origin_date.replace(year=target_year, month=target_month, day=calendar.monthrange(
            target_year, target_month)[1], hour=23, minute=59, second=59)

        totalStock = Order.objects.filter(
            (
                Q(payment_date__gte=range_start) &
                Q(payment_date__lte=range_end)
            ) &
            Q(store=self) &
            Q(payment_status=EATPLE_ORDER_STATUS_PAID)
        ).count()

        return totalStock

    def getPrevPrevMonthStock(self):
        return self.getMontlyStock(2)

    def getPrevMonthStock(self):
        return self.getMontlyStock(1)

    def getTotalStock(self):
        totalStock = Order.objects.filter(
            store=self, payment_status=EATPLE_ORDER_STATUS_PAID).count()

        return totalStock

    def getPrevPrevIncreaseStock(self):
        return self.getPrevPrevMonthStock() - self.getMontlyStock(3)

    def getPrevIncreaseStock(self):
        return self.getPrevMonthStock() - self.getPrevPrevMonthStock()

    def getCurrentIncreaseStock(self):
        return self.getMontlyStock() - self.getPrevMonthStock()

    def __str__(self):
        return '{name}'.format(name=self.name)
