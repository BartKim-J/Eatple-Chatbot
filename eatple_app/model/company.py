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
from eatple_app.model.utils import b2b_logo_directory_path

DEFAULT_LOGO_IMAGE_PATH = 'STORE_DB/images/default/logo.png'


class CompanyPlace(models.Model):
    class Meta:
        verbose_name = "위치"
        verbose_name_plural = "위치"

    company = models.OneToOneField(
        'Company',
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

        if(self.company != None):
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


class CompanyCRN(models.Model):
    class Meta:
        verbose_name = "사업자 등록번호"
        verbose_name_plural = "사업자 등록번호"

    company = models.OneToOneField(
        'Company',
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
        verbose_name="사업자 등록번호"
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
        super(CompanyCRN, self).__init__(*args, **kwargs)

        self.CRN_id = '{}{}{}{}'.format(
            self.UID,
            self.CC,
            self.SN,
            self.VN
        )

        super(CompanyCRN, self).save()

    def __str__(self):
        return '{UID}-{CC}-{SN}{VN}'.format(
            UID=self.UID,
            CC=self.CC,
            SN=self.SN,
            VN=self.VN
        )


class CompanyInfo(models.Model):
    company_id = models.CharField(
        default='N/A',
        max_length=WORD_LENGTH,
        unique=True,
        verbose_name="B2B 제휴 업체 고유 번호"
    )

    name = models.CharField(
        max_length=WORD_LENGTH,
        verbose_name="상호"
    )

    addr = models.CharField(
        max_length=WORD_LENGTH,
        verbose_name="주소"
    )

    phone_number = PhoneNumberField(
        max_length=WORD_LENGTH,
        null=True,
        blank=True,
        verbose_name="담당자 전화번호"
    )

    class Meta:
        abstract = True


class CompanySetting(models.Model):
    class Meta:
        verbose_name = "설정"
        verbose_name_plural = "설정"

        abstract = True

    logo = models.ImageField(
        default=DEFAULT_LOGO_IMAGE_PATH,
        blank=True,
        upload_to=b2b_logo_directory_path,
        storage=OverwriteStorage(),
        verbose_name="로고 이미지"
    )

    notice = models.TextField(
        blank=True,
        verbose_name="공지사항"
    )


class CompanyStatus(models.Model):
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


class Company(CompanyInfo, CompanySetting, CompanyStatus):
    class Meta:
        verbose_name = "B2B 제휴 업체"
        verbose_name_plural = "B2B 제휴 업체"

        ordering = ['-name']

    def __init__(self, *args, **kwargs):
        super(Company, self).__init__(*args, **kwargs)

        if (self.id == None):
            try:
                self.id = Company.objects.latest('id').id + 1
            except (Company.DoesNotExist) as ex:
                self.id = 1

        self.company_id = '{area:04X}-{id:04X}'.format(area=0, id=self.id)

    def logoImgURL(self):
        try:
            return self.logo.url
        except ValueError:
            return DEFAULT_LOGO_IMAGE_PATH

    def __str__(self):
        return '{name}'.format(name=self.name)
