
# Django Library
from eatple_app.models import Store, Menu
from eatple_app.models import Category, Tag
from eatple_app.models import Order
from django.urls import reverse
from django.db import models
from django_mysql.models import Model

# External Library

# Define
from eatple_app.define import *


class KakaoUser(models.Model):
    app_user_id = models.IntegerField(
        default=0,
        verbose_name = "카카오 고유 번호"
    )
    
    nickname = models.CharField(
        max_length=WORD_LENGTH, 
        null=True,
        verbose_name = "카카오 닉네임"
    )
    
    phone_number = PhoneNumberField(
        max_length=WORD_LENGTH, 
        null=True,
        verbose_name = "전화번호"
    )

    email = models.CharField(
        max_length=WORD_LENGTH, 
        null=True,
        verbose_name = "이메일"
    )

    birthyear = models.CharField(
        max_length=WORD_LENGTH, 
        null=True,
        verbose_name = "생년"
    )
    birthday = models.CharField(
        max_length=WORD_LENGTH, 
        null=True,
        verbose_name = "생일"
    )
    
    gender = models.CharField(
        max_length=WORD_LENGTH, 
        null=True,
        verbose_name = "성별"
    )
    
    ci = models.CharField(
        max_length=STRING_LENGTH, 
        null=True,
    )
    ci_authenticated_at = models.CharField(
        max_length=STRING_LENGTH, 
        null=True 
    )
    
    class Meta:
        abstract = True
        
class Partner(KakaoUser, models.Model):
    class Meta:
        verbose_name = "유저 - 파트너"
        verbose_name_plural = "유저 - 파트너"
        
        ordering = ['-store__name']
    
    store = models.ForeignKey(
        'Store', 
        on_delete=models.CASCADE, 
        null=True,
        verbose_name = "상점"
    )

    type = models.CharField(
        max_length=WORD_LENGTH, 
        default=PARTNER_TYPE_NORMAL,
        choices=PARTNER_TYPE,
        verbose_name = "권한"
    )

    is_inactive = models.BooleanField(
        default=False,
        verbose_name="비활성화"
    )

    is_staff = models.BooleanField(
        default=False,
        verbose_name="스태프"
    )

    create_date = models.DateTimeField(
        auto_now=True,
        verbose_name = "가입일자"
    )

    @classmethod
    def signUp(cls, *args, **kwargs):
        registedUser = cls(*args, **kwargs)
        registedUser.save()

        return registedUser

    def storeRegistration(self, store):
        self.store = store
        super().save()
        
        return store

        # Methods
    def __str__(self):
        if(self.store == None):
            store_name = "N/A"
        else:
            store_name = self.store.name
            
        return '{} : {}'.format(store_name, self.app_user_id)
