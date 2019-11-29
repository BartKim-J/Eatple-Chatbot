# Django Library
from django.urls import reverse
from django.db import models
from django.db.models import Q
from django_mysql.models import Model
from django.utils import timezone

# Define
from eatple_app.define import *


class OrderRecord(models.Model):
    class Meta:
        ordering = ['-record_date']

    order_record_sheet = models.ForeignKey(
        'OrderRecordSheet',
        on_delete=models.CASCADE,
        null=True
    )

    status = models.IntegerField(
        choices=ORDER_RECORD,
        null=True
    )

    record_date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return "{}".format(self.order_record_sheet)


class OrderRecordSheet(models.Model):
    class Meta:
        ordering = ['-update_date']

    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        null=True
    )

    menu = models.ForeignKey(
        'Menu',
        on_delete=models.CASCADE,
        null=True
    )

    update_date = models.DateTimeField(auto_now=True)
    created_date = models.DateTimeField(auto_now_add=True)

    status = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        isVertification = True

        if(self.user == None):
            isVertification = False

        elif(self.menu == None):
            isVertification = False

        self.status = isVertification

        super().save(*args, **kwargs)

    def recordUpdate(self, status, *args, **kwargs):
        if(self.id == None):
            super().save(*args, **kwargs)
            
        timeOut = False
        latest_date = dateByTimeZone(self.update_date)
        current_date = dateNowByTimeZone()

        if(latest_date + timedelta(minutes=3) < current_date):
            return True

        super().save(*args, **kwargs)

        orderRecord = OrderRecord(order_record_sheet=self, status=status)
        orderRecord.save()

        return timeOut

    # Methods
    def __str__(self):
        return "{}".format(self.user)
