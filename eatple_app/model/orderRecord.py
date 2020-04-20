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
        ordering = ['record_date']
        verbose_name = "레코드"
        verbose_name_plural = "레코드"

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
        super().save()

    def __str__(self):
        return '{}'.format(self.order_record_sheet)


class OrderRecordSheet(models.Model):
    class Meta:
        verbose_name = "주문 레코드 시트"
        verbose_name_plural = "주문 레코드 시트"

        ordering = ['-update_date']

    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        null=True,
        verbose_name="사용자"
    )

    order = models.ForeignKey(
        'Order',
        on_delete=models.CASCADE,
        null=True,
        verbose_name="주문 번호"
    )

    paid = models.BooleanField(
        default=False,
        verbose_name="결제 완료 여부"
    )

    status = models.BooleanField(
        default=False,
        verbose_name="메뉴 선택 여부"
    )

    update_date = models.DateTimeField(
        auto_now=True,
        verbose_name="마지막 기록 시간"
    )

    created_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="주문 시작 시간"
    )

    def recordUpdate(self, user, order, status, *args, **kwargs):
        isVertification = True

        if(user != None and order != None):
            self.user = user
            self.order = order
        else:
            isVertification = False

        if(self.user == None):
            isVertification = False

        elif(self.order == None):
            if(self.order.menu == None):
                isVertification = False

        print("Order Record : {}".format(dict(ORDER_RECORD)[status]))

        self.status = isVertification
        self.save()

        orderRecord = OrderRecord(order_record_sheet=self, status=status)
        orderRecord.save()

    def timeoutValidation(self):
        timeOut = False

        if(ORDER_TIME_CHECK_DEBUG_MODE):
            deadline = dateNowByTimeZone() + \
                datetime.timedelta(minutes=30)
        else:
            deadline = dateByTimeZone(self.update_date) + \
                datetime.timedelta(minutes=30)
                
        current_date = dateNowByTimeZone()

        if (deadline < current_date):
            timeOut = True

        print("Time Out : {}, {} < {}".format(timeOut, deadline, current_date))
        return timeOut

    # Methods
    def __str__(self):
        return '{}'.format(self.user)
