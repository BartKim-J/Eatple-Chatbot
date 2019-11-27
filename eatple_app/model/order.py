'''
    Author : Ben Kim

    @NOTE
    @BUG
    @TODO

'''
# Django Library
from django.urls import reverse
from django.db import models
from django_mysql.models import Model
from django.utils import timezone

# External Library
from datetime import datetime, timedelta

# Define
from eatple_app.define import EP_define, dateNowByTimeZone, dateByTimeZone

NOT_APPLICABLE = EP_define.NOT_APPLICABLE
DEFAULT_OBJECT_ID = EP_define.DEFAULT_OBJECT_ID

SELLING_TIME_LUNCH = EP_define.SELLING_TIME_LUNCH
SELLING_TIME_DINNER = EP_define.SELLING_TIME_DINNER
SELLING_TIME_CATEGORY_DICT = EP_define.SELLING_TIME_CATEGORY_DICT
SELLING_TIME_CATEGORY = EP_define.SELLING_TIME_CATEGORY

ORDER_STATUS_DICT = EP_define.ORDER_STATUS_DICT
ORDER_STATUS = EP_define.ORDER_STATUS

MANAGEMENT_CODE_LENGTH = EP_define.MANAGEMENT_CODE_LENGTH
STRING_LENGTH = EP_define.STRING_LENGTH

MANAGEMENT_CODE_DEFAULT = EP_define.MANAGEMENT_CODE_DEFAULT

# Static Functions


def orderStatusUpdateByTime(orderInstance):
    menuInstance = orderInstance.menuInstance

    orderDate = dateByTimeZone(orderInstance.order_date)
    orderDateWithoutTime = orderDate.replace(
        hour=0, minute=0, second=0, microsecond=0)

    orderPickupTime = orderInstance.pickupTime

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
            orderInstance.status = ORDER_STATUS[ORDER_STATUS_DICT['픽업 준비중']][0]
            orderInstance.save()
        # PickupTime Range
        elif(lunchOrderPickupTimeStart <= currentDate) and (currentDate <= lunchOrderPickupTimeEnd):
            # Over Order Pickup Time
            if(currentDate >= orderPickupTime):
                orderInstance.status = ORDER_STATUS[ORDER_STATUS_DICT['픽업 가능']][0]
                orderInstance.save()
            else:
                orderInstance.status = ORDER_STATUS[ORDER_STATUS_DICT['픽업 준비중']][0]
                orderInstance.save()
        # Order Time Range
        else:
            # prev phase Order
            if(prevlunchOrderEditTimeStart <= currentDate) and (currentDate <= prevlunchOrderTimeEnd):
                if currentDate <= prevlunchOrderEditTimeEnd:
                    orderInstance.status = ORDER_STATUS[ORDER_STATUS_DICT['주문 완료']][0]
                    orderInstance.save()

                else:
                    orderInstance.status = ORDER_STATUS[ORDER_STATUS_DICT['픽업 준비중']][0]
                    orderInstance.save()

            # next phase Lunch order
            elif (nextlunchOrderTimeEnd >= currentDate) and (orderDateWithoutTime >= TODAY):
                orderInstance.status = ORDER_STATUS[ORDER_STATUS_DICT['주문 완료']][0]
                orderInstance.save()

            # Invalid Time Range is Dinner Order Time ( prev phase lunch order ~ dinner order ~ next phase lunch order )
            else:
                orderInstance.status = ORDER_STATUS[ORDER_STATUS_DICT['주문 만료']][0]
                orderInstance.save()

    # Dinner Order
    elif (SELLING_TIME_CATEGORY[SELLING_TIME_DINNER][0] == menuInstance.sellingTime) and (orderDateWithoutTime == TODAY):
        # Meal Pre-
        if(dinnerOrderTimeEnd <= currentDate) and (currentDate <= dinnerOrderPickupTimeStart):
            orderInstance.status = ORDER_STATUS[ORDER_STATUS_DICT['픽업 준비중']][0]
            orderInstance.save()
        # PickupTime Range
        elif(dinnerOrderPickupTimeStart <= currentDate) and (currentDate <= dinnerOrderPickupTimeEnd):
            # Over Order Pickup Time
            if(currentDate >= orderPickupTime):
                orderInstance.status = ORDER_STATUS[ORDER_STATUS_DICT['픽업 가능']][0]
                orderInstance.save()
            else:
                orderInstance.status = ORDER_STATUS[ORDER_STATUS_DICT['픽업 준비중']][0]
                orderInstance.save()
        else:
            # Today Order
            if(dinnerOrderEditTimeStart < currentDate) and (currentDate < dinnerOrderTimeEnd):

                if orderDate <= dinnerOrderEditTimeEnd:
                    orderInstance.status = ORDER_STATUS[ORDER_STATUS_DICT['주문 완료']][0]
                    orderInstance.save()

                else:
                    orderInstance.status = ORDER_STATUS[ORDER_STATUS_DICT['픽업 준비중']][0]
                    orderInstance.save()
            # Invalid Time Range is Lunch Order Time ( prev phase lunch order ~ dinner order ~ next phase lunch order )
            else:
                orderInstance.status = ORDER_STATUS[ORDER_STATUS_DICT['주문 만료']][0]
                orderInstance.save()

    # Invalid Order Selling Time
    else:
        orderInstance.status = ORDER_STATUS[ORDER_STATUS_DICT['주문 만료']][0]
        orderInstance.save()

    return orderInstance.status


def OrderManagementCodeGenerator(storeInstance, menuInstance, userInstance, order_date):
    management_code = ''
    management_code += '{:02d}'.format(storeInstance.id % 10)
    management_code += '{:02d}'.format(menuInstance.id % 10)
    management_code += '{:02d}'.format(userInstance.id % 10)
    management_code += order_date.strftime("%M%H%S")

    return management_code

# Models


class OrderForm(models.Model):
    userInstance = models.ForeignKey(
        'User',  on_delete=models.DO_NOTHING, default=DEFAULT_OBJECT_ID)
    
    order_date = models.DateTimeField(default=timezone.now)

    # Methods
    def __str__(self):
        return "[ Order Box ] : {}".format(self.order_date)


class Order(models.Model):
    class Meta:
        ordering = ['-pickupTime']

    OrderFormInstance = models.ForeignKey(
        'OrderForm',  on_delete=models.DO_NOTHING, default=DEFAULT_OBJECT_ID)
    userInstance = models.ForeignKey(
        'User',  on_delete=models.DO_NOTHING, default=DEFAULT_OBJECT_ID)
    storeInstance = models.ForeignKey(
        'Store',  on_delete=models.DO_NOTHING, default=DEFAULT_OBJECT_ID)
    menuInstance = models.ForeignKey(
        'Menu',  on_delete=models.DO_NOTHING, default=DEFAULT_OBJECT_ID)

    management_code = models.CharField(max_length=MANAGEMENT_CODE_LENGTH, blank=True, null=True,
                                       help_text="Menu Magement Code")

    pickupTime = models.DateTimeField(default=timezone.now)

    update_date = models.DateTimeField(auto_now_add=False, auto_now=True)
    order_date = models.DateTimeField(default=timezone.now)

    status = models.CharField(max_length=STRING_LENGTH, choices=ORDER_STATUS,
                              default=ORDER_STATUS[ORDER_STATUS_DICT['주문 완료']][0])

    @classmethod
    def pushOrder(cls, userInstance, storeInstance, menuInstance, pickupTime):
        orderDate = dateNowByTimeZone()
        orderDateWithoutTime = orderDate.replace(
            hour=0, minute=0, second=0, microsecond=0)

        pickupTime = cls.rowPickupTimeToDatetime(pickupTime)

        # Next Lunch Order Edit Time 16:30 ~ 9:30(~ 10:30)
        nextlunchOrderEditTimeStart = orderDateWithoutTime + \
            timedelta(hours=16, minutes=30)
        nextlunchOrderTimeEnd = orderDateWithoutTime + \
            timedelta(hours=10, minutes=30, days=1)

        if(nextlunchOrderEditTimeStart <= orderDate) and (orderDate <= nextlunchOrderTimeEnd):
            pickupTime = pickupTime + timedelta(days=1)

        managementCode = OrderManagementCodeGenerator(
            storeInstance, menuInstance, userInstance, orderDate)

        pushedOrder = cls(userInstance=userInstance, storeInstance=storeInstance, menuInstance=menuInstance,
                          management_code=managementCode, pickupTime=pickupTime, order_date=orderDate)
        pushedOrder.save()

        return pushedOrder

    @staticmethod
    def rowPickupTimeToDatetime(rowPickupTime):
        return dateNowByTimeZone().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(hours=int(rowPickupTime[0:2]), minutes=int(rowPickupTime[3:5]))

    # Methods
    def __str__(self):
        return "[ Order ] {} - {} :: {} ----- {}".format(self.management_code, self.status, self.pickupTime, self.order_date)


class storeOrderManager():
    def __init__(self, storeId):
        self.storeOrderList = Order.objects.filter(storeInstance__id=storeId)

    def availableCouponStatusUpdate(self):
        availableCoupons = self.getAvailableCoupons()

        print(availableCoupons)

        # Order Status Update
        for orderInstance in availableCoupons:
            orderStatusUpdateByTime(orderInstance)

        return self.getAvailableCoupons()

    def getUnavailableCoupons(self):
        unavailableCoupons = self.storeOrderList.exclude(
            status=ORDER_STATUS[ORDER_STATUS_DICT['주문 확인중']][0]
        ).exclude(
            status=ORDER_STATUS[ORDER_STATUS_DICT['주문 완료']][0]
        ).exclude(
            status=ORDER_STATUS[ORDER_STATUS_DICT['픽업 준비중']][0]
        ).exclude(
            status=ORDER_STATUS[ORDER_STATUS_DICT['픽업 가능']][0]
        )
        return unavailableCoupons

    def getAvailableCoupons(self):
        availableCoupons = self.storeOrderList.exclude(
            status=ORDER_STATUS[ORDER_STATUS_DICT['픽업 완료']][0]
        ).exclude(
            status=ORDER_STATUS[ORDER_STATUS_DICT['주문 만료']][0]
        ).exclude(
            status=ORDER_STATUS[ORDER_STATUS_DICT['주문 취소']][0]
        )
        return availableCoupons


class OrderManager():
    def __init__(self, userID):
        self.userOrderList = Order.objects.filter(
            userInstance__identifier_code=userID)

    def availableCouponStatusUpdate(self):
        availableCoupons = self.getAvailableCoupons()

        # Order Status Update
        for orderInstance in availableCoupons:
            orderStatusUpdateByTime(orderInstance)

        return self.getAvailableCoupons()

    def getUnavailableCoupons(self):
        unavailableCoupons = self.userOrderList.exclude(
            status=ORDER_STATUS[ORDER_STATUS_DICT['주문 확인중']][0]
        ).exclude(
            status=ORDER_STATUS[ORDER_STATUS_DICT['주문 완료']][0]
        ).exclude(
            status=ORDER_STATUS[ORDER_STATUS_DICT['픽업 준비중']][0]
        ).exclude(
            status=ORDER_STATUS[ORDER_STATUS_DICT['픽업 가능']][0]
        )
        return unavailableCoupons

    def getAvailableCoupons(self):
        availableCoupons = self.userOrderList.exclude(
            status=ORDER_STATUS[ORDER_STATUS_DICT['픽업 완료']][0]
        ).exclude(
            status=ORDER_STATUS[ORDER_STATUS_DICT['주문 만료']][0]
        ).exclude(
            status=ORDER_STATUS[ORDER_STATUS_DICT['주문 취소']][0]
        )
        return availableCoupons

    def getAvailableLunchCouponPurchased(self):
        availableCoupons = self.getAvailableCoupons()
        lunchCoupons = availableCoupons.filter(
            menuInstance__sellingTime=SELLING_TIME_CATEGORY[SELLING_TIME_LUNCH][0])
        return lunchCoupons

    def getAvailableDinnerCouponPurchased(self):
        availableCoupons = self.getAvailableCoupons()
        dinnerCoupons = availableCoupons.filter(
            menuInstance__sellingTime=SELLING_TIME_CATEGORY[SELLING_TIME_DINNER][0])
        return dinnerCoupons
