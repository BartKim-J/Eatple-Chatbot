#-*- coding: utf-8 -*-

from django.db import models
from django_mysql.models import Model

from jsonfield import JSONField

STRING_LENGHT = 255


class Store(models.Model):
    store_name = models.CharField(max_length=STRING_LENGHT, help_text="상호명")
    store_addr = models.CharField(max_length=STRING_LENGHT, help_text="주소") 
    owner_name = models.CharField(max_length=STRING_LENGHT, help_text="가맹주")

    store_logo = models.ImageField(blank=True, upload_to="eatplus_chatot_app/DB/logo_img")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Menu:
        menu_name = models.CharField(max_length=STRING_LENGHT, help_text="메뉴명")
        
        def __str__(self):
            print(self.menu_name)
            return self.menu_name

    def as_json(self):
        return dict(
            store_name=self.store_name,
            store_addr=self.store_addr,
            owner_name=self.owner_name,
            created_at=self.created_at,
            updated_at=self.updated_at,
            )

    def publish(self):
        self.updated_at = models.DateTimeField(auto_now=True)
        self.save()

    def __str__(self):
        print(self.store_name)
        return self.store_name