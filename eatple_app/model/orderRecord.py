# Django Library
from django.urls import reverse
from django.db import models
from django.db.models import Q
from django_mysql.models import Model
from django.utils import timezone

# External Library
from datetime import datetime, timedelta

# Define
from eatple_app.define import *

class OrderRecord(models.Model):
    class Meta:
        ordering = ['-update_date']

    order_record_sheet = models.ForeignKey(
        'OrderRecordSheet',
        on_delete=models.DO_NOTHING,
        default=DEFAULT_OBJECT_ID,
        null=True
    )

    update_date = models.DateTimeField(auto_now_add=False, auto_now=True)
    created_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return "{}".format(self.order_record_sheet)


class OrderRecordSheet(models.Model):
    class Meta:
        ordering = ['-update_date']

    user = models.ForeignKey(
        'User',
        on_delete=models.DO_NOTHING,
        default=DEFAULT_OBJECT_ID,
        null=True
    )

    menu = models.ForeignKey(
        'Menu',
        on_delete=models.DO_NOTHING,
        default=DEFAULT_OBJECT_ID,
        null=True
    )

    update_date = models.DateTimeField(auto_now_add=False, auto_now=True)
    created_date = models.DateTimeField(default=timezone.now)

    status = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        isVertification = True

        if(self.user == None):
            isVertification = False

        elif(self.menu == None):
            isVertification = False

        self.status = isVertification

        super().save(*args, **kwargs)

    # Methods
    def __str__(self):
        return "{}".format(self.user)
