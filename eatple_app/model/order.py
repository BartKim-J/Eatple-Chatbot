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

def orderStatusUpdateByTime(order):
    menuInstance = order.menuInstance

    orderDate = dateByTimeZone(order.order_date)
    orderDateWithoutTime = orderDate.replace(
        hour=0, minute=0, second=0, microsecond=0)

    orderPickupTime = order.pickupTime

    currentDate = dateNowByTimeZone()
    currentDateWithoutTime = currentDate.replace(
        hour=0, minute=0, second=0, microsecond=0)

    YESTERDAY = currentDateWithoutTime + timedelta(days=-1)  # Yesterday start
    TODAY = currentDateWithoutTime
    TOMORROW = currentDateWithoutTime + timedelta(days=1)  # Tommorrow start

    # Prev Lunch Order Edit Time 16:30 ~ 9:30(~ 10:30)
    prevlunchOrderEditTimeStart = currentDateWithoutTime + \
        timedelta(hours=16, minutes=30, days=-1)
    prevlunchOrderEditTimeEnd = currentDateWithoutTime + \
        timedelta(hours=9, minutes=30)
    prevlunchOrderTimeEnd = currentDateWithoutTime + \
        timedelta(hours=10, minutes=30)

    # Dinner Order Edit Time 10:30 ~ 15:30(~ 16:30)
    dinnerOrderEditTimeStart = currentDateWithoutTime + \
        timedelta(hours=10, minutes=30)
    dinnerOrderEditTimeEnd = currentDateWithoutTime + \
        timedelta(hours=15, minutes=30)
    dinnerOrderTimeEnd = currentDateWithoutTime + \
        timedelta(hours=16, minutes=30)

    # Next Lunch Order Edit Time 16:30 ~ 9:30(~ 10:30)
    nextlunchOrderEditTimeStart = currentDateWithoutTime + \
        timedelta(hours=16, minutes=30)
    nextlunchOrderEditTimeEnd = currentDateWithoutTime + \
        timedelta(hours=9, minutes=30, days=1)
    nextlunchOrderTimeEnd = currentDateWithoutTime + \
        timedelta(hours=10, minutes=30, days=1)

    # Lunch Order Pickup Time (10:30 ~)11:30 ~ 13:30
    lunchOrderPickupTimeStart = currentDateWithoutTime + \
        timedelta(hours=11, minutes=30)
    lunchOrderPickupTimeEnd = currentDateWithoutTime + \
        timedelta(hours=13, minutes=30)

    # Dinner Order Pickup Time (16:30 ~)17:30 ~ 21:00
    dinnerOrderPickupTimeStart = currentDateWithoutTime + \
        timedelta(hours=17, minutes=30)
    dinnerOrderPickupTimeEnd = currentDateWithoutTime + \
        timedelta(hours=21, minutes=0)

    # Lunch Order
    if (SELLING_TIME_CATEGORY[SELLING_TIME_LUNCH][0] == menuInstance.sellingTime) and \
            ((YESTERDAY <= orderDateWithoutTime) and (orderDateWithoutTime <= TODAY)):

        # Meal Pre-
        if(prevlunchOrderTimeEnd <= currentDate) and (currentDate <= lunchOrderPickupTimeStart):
            order.status = ORDER_STATUS[ORDER_STATUS_DICT['픽업 준비중']][0]
            order.save()
        # PickupTime Range
        elif(lunchOrderPickupTimeStart <= currentDate) and (currentDate <= lunchOrderPickupTimeEnd):
            # Over Order Pickup Time
            if(currentDate >= orderPickupTime):
                order.status = ORDER_STATUS[ORDER_STATUS_DICT['픽업 가능']][0]
                order.save()
            else:
                order.status = ORDER_STATUS[ORDER_STATUS_DICT['픽업 준비중']][0]
                order.save()
        # Order Time Range
        else:
            # prev phase Order
            if(prevlunchOrderEditTimeStart <= currentDate) and (currentDate <= prevlunchOrderTimeEnd):
                if currentDate <= prevlunchOrderEditTimeEnd:
                    order.status = ORDER_STATUS[ORDER_STATUS_DICT['주문 완료']][0]
                    order.save()

                else:
                    order.status = ORDER_STATUS[ORDER_STATUS_DICT['픽업 준비중']][0]
                    order.save()

            # next phase Lunch order
            elif (nextlunchOrderTimeEnd >= currentDate) and (orderDateWithoutTime >= TODAY):
                order.status = ORDER_STATUS[ORDER_STATUS_DICT['주문 완료']][0]
                order.save()

            # Invalid Time Range is Dinner Order Time ( prev phase lunch order ~ dinner order ~ next phase lunch order )
            else:
                order.status = ORDER_STATUS[ORDER_STATUS_DICT['주문 만료']][0]
                order.save()

    # Dinner Order
    elif (SELLING_TIME_CATEGORY[SELLING_TIME_DINNER][0] == menuInstance.sellingTime) and (orderDateWithoutTime == TODAY):
        # Meal Pre-
        if(dinnerOrderTimeEnd <= currentDate) and (currentDate <= dinnerOrderPickupTimeStart):
            order.status = ORDER_STATUS[ORDER_STATUS_DICT['픽업 준비중']][0]
            order.save()
        # PickupTime Range
        elif(dinnerOrderPickupTimeStart <= currentDate) and (currentDate <= dinnerOrderPickupTimeEnd):
            # Over Order Pickup Time
            if(currentDate >= orderPickupTime):
                order.status = ORDER_STATUS[ORDER_STATUS_DICT['픽업 가능']][0]
                order.save()
            else:
                order.status = ORDER_STATUS[ORDER_STATUS_DICT['픽업 준비중']][0]
                order.save()
        else:
            # Today Order
            if(dinnerOrderEditTimeStart < currentDate) and (currentDate < dinnerOrderTimeEnd):

                if orderDate <= dinnerOrderEditTimeEnd:
                    order.status = ORDER_STATUS[ORDER_STATUS_DICT['주문 완료']][0]
                    order.save()

                else:
                    order.status = ORDER_STATUS[ORDER_STATUS_DICT['픽업 준비중']][0]
                    order.save()
            # Invalid Time Range is Lunch Order Time ( prev phase lunch order ~ dinner order ~ next phase lunch order )
            else:
                order.status = ORDER_STATUS[ORDER_STATUS_DICT['주문 만료']][0]
                order.save()

    # Invalid Order Selling Time
    else:
        order.status = ORDER_STATUS[ORDER_STATUS_DICT['주문 만료']][0]
        order.save()

    return order.status


class Order(models.Model):
    class Meta:
        ordering = ['-pickup_time']

    order_code = models.CharField(
        max_length=MANAGEMENT_CODE_LENGTH,
        blank=True,
        null=True
    )

    ordersheet = models.ForeignKey(
        'OrderSheet',
        on_delete=models.CASCADE,
        default=DEFAULT_OBJECT_ID
    )

    store = models.ForeignKey(
        'Store',
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

    count = models.IntegerField(default=1)

    pickup_time = models.DateTimeField(auto_now=True)

    update_date = models.DateTimeField(auto_now=True)
    order_date = models.DateTimeField(auto_now_add=True)

    status = models.IntegerField(
        # max_length=STRING_LENGTH,
        choices=ORDER_STATUS,
        default=ORDER_STATUS_PAYMENT_WAIT,
    )

    def __init__(self, *args, **kwargs):
        super(Order, self).__init__(*args, **kwargs)

        if (self.id == None):
            try:
                self.id = Order.objects.latest('id').id + 1
            except (Order.DoesNotExist) as ex:
                self.id = 1

        self.order_code = "EP{area:08X}{id:04X}".format(
            area=int(self.order_date.strftime('%f')), id=self.id)

    @staticmethod
    def rowPickupTimeToDatetime(rowPickupTime):
        return dateNowByTimeZone().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(hours=int(rowPickupTime[0:2]), minutes=int(rowPickupTime[3:5]))

    # Methods

    def __str__(self):
        return "{}".format(self.order_code)

class storeOrderManager():
    def __init__(self, storeId):
        self.storeOrderList = Order.objects.filter(storeInstance__id=storeId)

    def availableOrderStatusUpdate(self):
        availableOrders = self.getAvailableOrders()

        print(availableOrders)

        # Order Status Update
        for order in availableOrders:
            orderStatusUpdateByTime(order)

        return self.getAvailableOrders()

    def getUnavailableOrders(self):
        unavailableOrders = self.storeOrderList.filter(
            ~Q(status=ORDER_STATUS_PAYMENT_COMPLETED) &
            ~Q(status=ORDER_STATUS_ORDER_CONFIRM_WAIT) &
            ~Q(status=ORDER_STATUS_PICKUP_PREPARE) &
            ~Q(status=ORDER_STATUS_PICKUP_WAIT)
        )
        return unavailableOrders

    def getAvailableOrders(self):
        availableOrders = self.storeOrderList.filter(
            Q(status=ORDER_STATUS_PAYMENT_COMPLETED) &
            Q(status=ORDER_STATUS_ORDER_CONFIRM_WAIT) &
            Q(status=ORDER_STATUS_PICKUP_PREPARE) &
            Q(status=ORDER_STATUS_PICKUP_WAIT)
        )
        return availableOrders

class OrderManager():
    def __init__(self, user):
        self.userOrderList = Order.objects.filter(
            ordersheet__user=user)

    def availableOrderStatusUpdate(self):
        availableOrders = self.getAvailableOrders()

        # Order Status Update
        for order in availableOrders:
            orderStatusUpdateByTime(order)

        return self.getAvailableOrders()

    def getUnavailableOrders(self):
        unavailableOrders = self.userOrderList.filter(
            ~Q(status=ORDER_STATUS_PAYMENT_COMPLETED) &
            ~Q(status=ORDER_STATUS_ORDER_CONFIRM_WAIT) &
            ~Q(status=ORDER_STATUS_PICKUP_PREPARE) &
            ~Q(status=ORDER_STATUS_PICKUP_WAIT)
        )
        return unavailableOrders

    def getAvailableOrders(self):
        availableOrders = self.userOrderList.filter(
            Q(status=ORDER_STATUS_PAYMENT_COMPLETED) &
            Q(status=ORDER_STATUS_ORDER_CONFIRM_WAIT) &
            Q(status=ORDER_STATUS_PICKUP_PREPARE) &
            Q(status=ORDER_STATUS_PICKUP_WAIT)
        )

        return availableOrders

    def getAvailableLunchuserOrderListPurchased(self):
        availableOrders = self.getAvailableOrders()
        lunchOrders = availableOrders.filter(
            menu__sellingTime=SELLING_TIME_CATEGORY[SELLING_TIME_LUNCH][0])
        return lunchOrders

    def getAvailableDinnerOrderPurchased(self):
        availableOrders = self.getAvailableOrders()
        dinnerOrders = availableOrders.filter(
            menu__sellingTime=SELLING_TIME_CATEGORY[SELLING_TIME_DINNER][0])
        return dinnerOrders

class OrderSheet(models.Model):
    class Meta:
        ordering = ['-order_date']

    user = models.ForeignKey(
        'User',  
        on_delete=models.DO_NOTHING, 
        default=DEFAULT_OBJECT_ID, 
        null=True
    )

    management_code = models.CharField(
        max_length=MANAGEMENT_CODE_LENGTH, 
        blank=True, 
        null=True
    )

    update_date = models.DateTimeField(auto_now=True)
    order_date = models.DateTimeField(auto_now_add=True)

    def __init__(self, *args, **kwargs):
        super(OrderSheet, self).__init__(*args, **kwargs)

        if (self.id == None):
            try:
                self.id = OrderSheet.objects.latest('id').id + 1
            except (OrderSheet.DoesNotExist) as ex:
                self.id = 1

        self.management_code = "E{area:06X}P{id:03x}".format(
            area=int(self.order_date.strftime('%f')), id=self.id)

    # Methods
    def __str__(self):
        return "{}".format(self.management_code)


