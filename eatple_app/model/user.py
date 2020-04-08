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


class Location(models.Model):
    class Meta:
        verbose_name = "위치"
        verbose_name_plural = "위치"

    user = models.OneToOneField(
        'User',
        on_delete=models.CASCADE,
        unique=True,
        null=True,
        verbose_name="사용자"
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

    address = models.CharField(
        default=LOCATION_DEFAULT_ADDR,
        max_length=STRING_LENGTH,
        null=True,
        verbose_name="주소"
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

        if(self.user != None):
            self.point = Point(0, 0)
            super().save()

            if(self.lat <= 0 or self.long <= 0):
                self.lat = LOCATION_DEFAULT_LAT
                self.long = LOCATION_DEFAULT_LNG
                self.address = LOCATION_DEFAULT_ADDR
            self.point = Point(y=float(self.lat), x=float(self.long))
            super().save()
        else:
            pass

    def __str__(self):
        return '{}, {}'.format(self.lat, self.long)


class KakaoUser(models.Model):
    app_user_id = models.IntegerField(
        default=0,
        verbose_name="카카오 고유 번호"
    )

    nickname = models.CharField(
        max_length=WORD_LENGTH,
        null=True,
        verbose_name="카카오 닉네임"
    )

    phone_number = PhoneNumberField(
        max_length=WORD_LENGTH,
        null=True,
        verbose_name="전화번호"
    )

    email = models.CharField(
        max_length=WORD_LENGTH,
        null=True,
        verbose_name="이메일"
    )

    birthyear = models.CharField(
        max_length=WORD_LENGTH,
        null=True,
        verbose_name="생일년도"
    )
    birthday = models.CharField(
        max_length=WORD_LENGTH,
        null=True,
        verbose_name="생일날짜"
    )

    gender = models.CharField(
        max_length=WORD_LENGTH,
        null=True,
        verbose_name="성별"
    )

    ci = models.CharField(
        max_length=STRING_LENGTH,
        null=True
    )
    ci_authenticated_at = models.CharField(
        max_length=STRING_LENGTH,
        null=True
    )

    # @PROTMOTINO
    flag_promotion = models.BooleanField(
        default=False,
        verbose_name="프로모션 참가여부"
    )

    is_beta_tester = models.BooleanField(
        default=False,
        verbose_name="베타 테스터"
    )

    class Meta:
        abstract = True


class User(KakaoUser, models.Model):
    class Meta:
        verbose_name = "유저 - 사용자"
        verbose_name_plural = "유저 - 사용자"

        ordering = ['-create_date']

    company = models.ForeignKey(
        'Company',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="소속 회사"
    )

    create_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="가입일자"
    )

    type = models.CharField(
        max_length=WORD_LENGTH,
        default=USER_TYPE_NORMAL,
        choices=USER_TYPE,
        verbose_name="계정 유형"
    )

    @classmethod
    def signUp(cls, *args, **kwargs):
        registedUser = cls(*args, **kwargs)
        registedUser.save()

        return registedUser

    # @PROTMOTION
    def applyPromotion(self):
        self.flag_promotion = True
        self.save()

    def cancelPromotion(self):
        self.flag_promotion = False
        self.save()

    # Methods
    def __str__(self):
        return '{}'.format(self.nickname)
