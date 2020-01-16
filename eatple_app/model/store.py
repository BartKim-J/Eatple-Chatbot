# define
from eatple_app.define import *
# Django Library
from django.contrib.gis.db import models
from django.conf import settings
from django.urls import reverse
from django.core.files.storage import FileSystemStorage
from django_mysql.models import Model
from django.core.validators import MaxValueValidator, MinValueValidator

# Utils
from eatple_app.model.utils import OverwriteStorage
from eatple_app.model.utils import logo_directory_path

DEFAULT_LOGO_IMAGE_PATH = 'STORE_DB/images/default/logo.png'

class Category(models.Model):
    # Metadata
    class Meta:
        # abstract = True
        verbose_name="분류"
        verbose_name_plural = "분류"
        
        ordering = ['-name']

    name = models.CharField(
        max_length=WORD_LENGTH, 
        verbose_name="분류"
    )

    # Methods
    def __str__(self):
        return '{}'.format(self.name)

class Place(models.Model):
    class Meta:
        verbose_name = "위치"
        verbose_name_plural = "위치"
        
    store = models.OneToOneField(
        'Store', 
        on_delete=models.CASCADE,
        unique=True, 
        null=True,
        verbose_name="상점"
    )
    
    lat = models.DecimalField(
        default=LOCATION_DEFAULT_LAT,
        max_digits=18, 
        decimal_places=14,
        verbose_name="위도"
    )

    long = models.DecimalField(
        default=LOCATION_DEFAULT_LNG,
        max_digits=18, 
        decimal_places=14,
        verbose_name="경도"
    )

    point = models.PointField(
        null=True, 
        blank=True, 
        srid=4326, 
        geography=False,
        verbose_name="위치"
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
        return '{}, {}'.format(self.lat, self.long)

class CRN(models.Model):
    store = models.OneToOneField(
        'Store', 
        on_delete=models.CASCADE, 
        unique=True, 
        null=True,
        verbose_name="상점"
    )

    CRN_id = models.CharField(
        max_length=10, 
        help_text='Unique ID',
        blank=True,
        null=True,
        verbose_name="CRN"
    )
    
    UID = models.CharField(
        max_length=3, 
        help_text='Unique ID',
        verbose_name="UID"
    )

    CC = models.CharField(
        max_length=2, 
        help_text='Corporation Classification Code',
        verbose_name="CC"
    )

    SN = models.CharField(
        max_length=4, 
        help_text='Serial Number',
        verbose_name="SN"
    )

    VN = models.CharField(
        max_length=1, 
        help_text='Vertification Number',
        verbose_name="VN"
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

class StoreInfo(models.Model):
    store_id = models.CharField(
        default='N/A',
        max_length=WORD_LENGTH, 
        unique=True,
        verbose_name="상점 고유 번호"
    )

    name = models.CharField(
        max_length=WORD_LENGTH, 
        verbose_name="상호"
    )

    addr = models.CharField(
        max_length=STRING_LENGTH,
        verbose_name="주소"
    )

    phone_number = PhoneNumberField(
        null=True,
        blank=True,
        verbose_name="관리자 전화번호"
    )
        
    owner = models.CharField(
        max_length=WORD_LENGTH, 
        verbose_name="점주명"
    )

    class Meta:
        abstract = True


class StoreSetting(models.Model):
    class Meta:
        verbose_name = "설정"
        verbose_name_plural = "설정"
        
        abstract = True

    category = models.ManyToManyField(
        'Category',
        verbose_name="가게 분류"    
    )

    description = models.TextField(
        blank=True,
        verbose_name="가게 설명"
    )

    logo = models.ImageField(
        default=DEFAULT_LOGO_IMAGE_PATH,
        blank=True, 
        upload_to=logo_directory_path, 
        storage=OverwriteStorage(),
        verbose_name="로고 이미지"
    )

class StoreStatus(models.Model):
    class Meta:
        verbose_name = "상태"
        verbose_name_plural = "상태"
        
        abstract = True
 
    status = models.CharField(
        max_length=WORD_LENGTH, 
        default=OC_OPEN,
        choices=OC_STATUS,
        verbose_name="상태"
    )
    
    
    type = models.CharField(
        max_length=WORD_LENGTH, 
        default=STORE_TYPE_NORMAL,
        choices=STORE_TYPE,
        verbose_name="유형"
    )


    area = models.CharField(
        max_length=WORD_LENGTH, 
        default=STORE_AREA_A_3,
        choices=STORE_AREA,
        verbose_name="지역코드"
    )
    

        
class Store(StoreInfo, StoreSetting, StoreStatus):
    class Meta:
        verbose_name = "제휴 점포"
        verbose_name_plural = "제휴 점포"
        
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

    def __str__(self):
        return '{name}'.format(name=self.name)
