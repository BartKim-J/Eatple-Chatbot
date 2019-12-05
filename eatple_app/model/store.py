# define
from eatple_app.define import *
# Django Library
from django.db import models
from django.contrib.gis.db import models
from django.conf import settings
from django.urls import reverse
from django.core.files.storage import FileSystemStorage
from django_mysql.models import Model
from django.core.validators import MaxValueValidator, MinValueValidator
from django import forms

# Utils
from eatple_app.model.utils import OverwriteStorage
from eatple_app.model.utils import logo_directory_path

DEFAULT_LOGO_IMAGE_PATH = 'STORE_DB/images/default/logoImg.png'

class Category(models.Model):
    # Metadata
    class Meta:
        # abstract = True
        ordering = ['-name']

    name = models.CharField(max_length=WORD_LENGTH, help_text='Category')

    # Methods
    def __str__(self):
        return '{}'.format(self.name)

class Place(models.Model):
    store = models.OneToOneField(
        'Store', 
        on_delete=models.CASCADE, 
        unique=True, 
        null=True
    )
    
    lat = models.DecimalField(
        default=0.00000000000000,
        max_digits=18, 
        decimal_places=14
    )

    long = models.DecimalField(
        default=0.00000000000000,
        max_digits=18, 
        decimal_places=14
    )

    point = models.PointField(
        null=True, 
        blank=True, 
        srid=4326, 
        verbose_name="Location"
    )

    def __str__(self):
        return '{}, {}'.format(self.lat, self.long)

class CRN(models.Model):
    store = models.OneToOneField(
        'Store', 
        on_delete=models.CASCADE, 
        unique=True, 
        null=True
    )

    CRN_id = models.CharField(
        max_length=10, 
        help_text='Unique ID',
        blank=True,
        null=True
    )
    
    UID = models.CharField(
        max_length=3, 
        help_text='Unique ID'
    )

    CC = models.CharField(
        max_length=2, 
        help_text='Corporation Classification Code'
    )

    SN = models.CharField(
        max_length=4, 
        help_text='Serial Number'
    )

    VN = models.CharField(
        max_length=1, 
        help_text='Vertification Number'
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
        help_text='상점 고유 번호*',
        unique=True
    )

    name = models.CharField(
        max_length=WORD_LENGTH, 
        help_text='상호*',
    )

    addr = models.CharField(
        max_length=WORD_LENGTH,
        help_text='주소*',
    )

    phone_number = PhoneNumberField(
        max_length=WORD_LENGTH, 
        null=True,
        blank=True,
        help_text='전화번호*',
    )
        
    owner = models.CharField(
        max_length=WORD_LENGTH, 
        help_text='점주명*'
    )

    class Meta:
        abstract = True


class StoreSetting(models.Model):
    category = models.ManyToManyField('Category')

    description = models.TextField(
        blank=True,
        help_text='가게 부가 정보*'
    )

    logo = models.ImageField(
        default=DEFAULT_LOGO_IMAGE_PATH,
        blank=True, 
        upload_to=logo_directory_path, 
        storage=OverwriteStorage(),
        help_text='로고*', 
    )

    class Meta:
        abstract = True

class StoreStatus(models.Model):
    status = models.CharField(
        max_length=WORD_LENGTH, 
        default=OC_OPEN,
        choices=OC_STATUS,
        help_text='가게 상태*', 
    )
    
    
    type = models.CharField(
        max_length=WORD_LENGTH, 
        default=STORE_TYPE_NORMAL,
        choices=STORE_TYPE,
        help_text='가게 유형*', 
    )
    
    area = models.CharField(
        max_length=WORD_LENGTH, 
        default=STORE_AREA_A_3,
        choices=STORE_AREA,
        help_text='가게 지역코드*', 
    )
    
    class Meta:
        abstract = True
        
class Store(StoreInfo, StoreSetting, StoreStatus):
    class Meta:
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
