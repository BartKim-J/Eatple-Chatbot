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

class userB2B(KakaoUser, models.Model):
    class Meta:
        verbose_name = "B2B 사용자 리스트"
        verbose_name_plural = "B2B 사용자 리스트"
        
        ordering = ['name']
    
    company = models.ForeignKey(
        'Company', 
        on_delete=models.CASCADE, 
        null=True,
        blank=True,
        verbose_name = "소속 회사"
    )

    name = models.CharField(
        max_length=MANAGEMENT_CODE_LENGTH,
        blank=True,
        null=True,
        verbose_name="이름"
    )
    
    phone_number = models.CharField(
        max_length=MANAGEMENT_CODE_LENGTH,
        blank=True,
        null=True,
        verbose_name="전화번호"
    )

    create_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name = "가입일자"
    )
        
    # Methods
    def __str__(self):
        return '{}'.format(self.nickname)
