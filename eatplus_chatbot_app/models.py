from django.db import models
from django_mysql.models import Model

from jsonfield import JSONField


class store(models.Model):
    store_name = models.CharField(max_length=32, db_column='상호', help_text="상호명", null=True,)
    store_addr = models.CharField(max_length=16, db_column='주소', help_text="주소", null=True) 
    owner_name = models.CharField(max_length= 8, db_column='가맹주', help_text="가맹주", null=True)

    store_logo = models.ImageField(blank=True, upload_to="eatplus_chatot_app/DB/logo_img")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    json_data = JSONField(
        default={},
    )

    def addMenu(self):
        self.updated_at = models.DateTimeField(auto_now=True)
        self.save()

    def publish(self):
        self.updated_at = models.DateTimeField(auto_now=True)
        self.save()

    def __str__(self):
        return self.store_name
