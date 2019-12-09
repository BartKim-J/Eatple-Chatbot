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
    user = models.OneToOneField(
        'User', 
        on_delete=models.CASCADE, 
        unique=True, 
        null=True
    )
    
    lat = models.DecimalField(
        default=LOCATION_DEFAULT_LAT,
        max_digits=18, 
        decimal_places=14
    )

    long = models.DecimalField(
        default=LOCATION_DEFAULT_LNG,
        max_digits=18, 
        decimal_places=14
    )
    
    address = models.CharField(
        default=LOCATION_DEFAULT_ADDR,
        max_length=STRING_LENGTH,
        null=True,
    )
    
    point = models.PointField(
        null=True, 
        blank=True, 
        srid=4326, 
        geography=False,
        verbose_name="Location"
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.point = Point(0, 0)
        super().save()
        
        if(self.lat <= 0 or self.long <= 0):
            self.lat = LOCATION_DEFAULT_LAT
            self.long = LOCATION_DEFAULT_LNG
        
        self.point = Point(y=float(self.lat), x=float(self.long))
        super().save()

    def __str__(self):
        return '{}, {}'.format(self.lat, self.long)

class KakaoUser(models.Model):
    app_user_id = models.IntegerField(default=0)
    
    nickname = models.CharField(
        max_length=WORD_LENGTH, null=True)
    
    phone_number = PhoneNumberField(
        max_length=WORD_LENGTH, null=True)

    email = models.CharField(
        max_length=WORD_LENGTH, null=True)

    birthyear = models.CharField(
        max_length=WORD_LENGTH, null=True)
    birthday = models.CharField(
        max_length=WORD_LENGTH, null=True)
    
    gender = models.CharField(
        max_length=WORD_LENGTH, null=True)
    
    ci = models.CharField(
        max_length=STRING_LENGTH, null=True)
    ci_authenticated_at = models.CharField(
        max_length=STRING_LENGTH, null=True )
    
    #@PROTMOTINO
    flag_promotion = models.BooleanField(default=False)
    
    class Meta:
        abstract = True

class User(KakaoUser, models.Model):
    class Meta:
        ordering = ['-app_user_id']
    
    create_date = models.DateTimeField(auto_now=True)

    @classmethod
    def signUp(cls, *args, **kwargs):
        registedUser = cls(*args, **kwargs)
        registedUser.save()

        return registedUser


    #@PROTMOTION
    def applyPromotion(self):
        self.flag_promotion = True;
        self.save()
        
    def cancelPromotion(self):
        self.flag_promotion = False;
        self.save()
        
    # Methods
    def __str__(self):
        return '{}'.format(self.app_user_id)
