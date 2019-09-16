#Django Library
from django.urls import reverse
from django.db import models
from django_mysql.models import Model
from django.utils import timezone

#External Library
from datetime import datetime, timedelta

#Models 
from .models_config import Config, dateNowByTimeZone

#GLOBAL CONFIG
NOT_APPLICABLE          = Config.NOT_APPLICABLE
DEFAULT_OBJECT_ID       = Config.DEFAULT_OBJECT_ID

SELLING_TIME_LUNCH          = Config.SELLING_TIME_LUNCH
SELLING_TIME_DINNER         = Config.SELLING_TIME_DINNER
SELLING_TIME_CATEGORY_DICT  = Config.SELLING_TIME_CATEGORY_DICT
SELLING_TIME_CATEGORY       = Config.SELLING_TIME_CATEGORY

ORDER_STATUS_DICT       = Config.ORDER_STATUS_DICT
ORDER_STATUS            = Config.ORDER_STATUS

MANAGEMENT_CODE_LENGTH  = Config.MANAGEMENT_CODE_LENGTH
STRING_LENGTH           = Config.STRING_LENGTH

MANAGEMENT_CODE_DEFAULT = Config.MANAGEMENT_CODE_DEFAULT


def orderStatusUpdateByTime(orderInstance):
    menuInstance              = orderInstance.menuInstance

    orderDate                 = orderInstance.order_date
    orderDateWithoutTime      = orderDate.replace(hour=0, minute=0, second=0, microsecond=0)

    orderPickupTime           = orderInstance.pickupTime
    
    nowDate                   = dateNowByTimeZone()
    nowDateWithoutTime        = nowDate.replace(hour=0, minute=0, second=0, microsecond=0)

    # Prev Lunch Order Edit Time 16:30 ~ 9:30(~ 10:30)
    prevlunchOrderEditTimeStart   = nowDateWithoutTime + timedelta(hours=16, minutes=30, days=-1)
    prevlunchOrderEditTimeEnd     = nowDateWithoutTime + timedelta(hours=9, minutes=30)
    prevlunchOrderTimeEnd         = nowDateWithoutTime + timedelta(hours=10, minutes=30)

    # Dinner Order Edit Time 10:30 ~ 15:30(~ 16:30)
    dinnerOrderEditTimeStart      = nowDateWithoutTime + timedelta(hours=10, minutes=30)
    dinnerOrderEditTimeEnd        = nowDateWithoutTime + timedelta(hours=15, minutes=30)
    dinnerOrderTimeEnd            = nowDateWithoutTime + timedelta(hours=16, minutes=30)

    # Next Lunch Order Edit Time 16:30 ~ 9:30(~ 10:30)
    nextlunchOrderEditTimeStart   = nowDateWithoutTime + timedelta(hours=16, minutes=30)
    nextlunchOrderEditTimeEnd     = nowDateWithoutTime + timedelta(hours=9, minutes=30, days=1)
    nextlunchOrderTimeEnd         = nowDateWithoutTime + timedelta(hours=10, minutes=30, days=1)

    # Lunch Order Pickup Time (10:30 ~)11:30 ~ 13:30
    lunchOrderPickupTimeStart     = nowDateWithoutTime + timedelta(hours=11, minutes=30)
    lunchOrderPickupTimeEnd       = nowDateWithoutTime + timedelta(hours=13, minutes=30)

    # Dinner Order Pickup Time (16:30 ~)17:30 ~ 21:00
    dinnerOrderPickupTimeStart    = nowDateWithoutTime + timedelta(hours=17, minutes=30)
    dinnerOrderPickupTimeEnd      = nowDateWithoutTime + timedelta(hours=21, minutes=0)

    # Lunch Order
    if SELLING_TIME_CATEGORY[SELLING_TIME_LUNCH][0] == menuInstance.sellingTime:
        # Out PickupTime Range
        if(prevlunchOrderTimeEnd <= nowDate) and (nowDate <= lunchOrderPickupTimeStart):
            orderInstance.status = ORDER_STATUS[ORDER_STATUS_DICT['픽업 준비중']][0]
            orderInstance.save()
        # In PickupTime Range
        elif(lunchOrderPickupTimeStart <= nowDate) and (nowDate <= lunchOrderPickupTimeEnd):
            # Over Order Pickup Time
            if(nowDate >= orderPickupTime):
                orderInstance.status = ORDER_STATUS[ORDER_STATUS_DICT['픽업 가능']][0]
                orderInstance.save()
            else:
                orderInstance.status = ORDER_STATUS[ORDER_STATUS_DICT['픽업 준비중']][0]
                orderInstance.save()
        else:
            # prev phase Order
            if(prevlunchOrderEditTimeStart <= nowDate) and (nowDate <= prevlunchOrderTimeEnd):
                if nowDate <= prevlunchOrderEditTimeEnd:
                    orderInstance.status = ORDER_STATUS[ORDER_STATUS_DICT['주문 완료']][0]
                    orderInstance.save()
                
                else:
                    orderInstance.status = ORDER_STATUS[ORDER_STATUS_DICT['픽업 준비중']][0]
                    orderInstance.save()

            # next phase Lunch order
            elif nextlunchOrderTimeEnd >= nowDate:
                orderInstance.status = ORDER_STATUS[ORDER_STATUS_DICT['주문 완료']][0]
                orderInstance.save()

            # Invalid Time Range is Dinner Order Time ( prev phase lunch order ~ dinner order ~ next phase lunch order )
            else:
                orderInstance.status = ORDER_STATUS[ORDER_STATUS_DICT['주문 만료']][0]
                orderInstance.save()

    # Dinner Order
    elif SELLING_TIME_CATEGORY[SELLING_TIME_DINNER][0] == menuInstance.sellingTime:
        # Out PickupTime Range
        if(dinnerOrderTimeEnd <= nowDate) and (nowDate <= dinnerOrderPickupTimeStart):
            orderInstance.status = ORDER_STATUS[ORDER_STATUS_DICT['픽업 준비중']][0]
            orderInstance.save()
        # In PickupTime Range
        elif(dinnerOrderPickupTimeStart <= nowDate) and (nowDate <= dinnerOrderPickupTimeEnd):
            # Over Order Pickup Time
            if(nowDate >= orderPickupTime):
                orderInstance.status = ORDER_STATUS[ORDER_STATUS_DICT['픽업 가능']][0]
                orderInstance.save()
            else:
                orderInstance.status = ORDER_STATUS[ORDER_STATUS_DICT['픽업 준비중']][0]
                orderInstance.save()
        else:
            # Today Order
            if(dinnerOrderEditTimeStart < nowDate) and (nowDate < dinnerOrderTimeEnd):

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

#STATIC CONFIG
class Order(models.Model):
    class Meta:
        ordering = ['-order_date']

    userInstance     = models.ForeignKey('User',  on_delete=models.DO_NOTHING, default=DEFAULT_OBJECT_ID)
    storeInstance    = models.ForeignKey('Store',  on_delete=models.DO_NOTHING, default=DEFAULT_OBJECT_ID)
    menuInstance     = models.ForeignKey('Menu',  on_delete=models.DO_NOTHING, default=DEFAULT_OBJECT_ID)

    management_code  = models.CharField(max_length=MANAGEMENT_CODE_LENGTH, blank=True, null=True,
                                        help_text="Menu Magement Code")

    pickupTime       = models.DateTimeField(default=timezone.now)

    update_date      = models.DateTimeField(auto_now_add=False, auto_now=True)
    order_date       = models.DateTimeField(default=timezone.now)

    status           = models.CharField(max_length=STRING_LENGTH, choices=ORDER_STATUS, default=ORDER_STATUS[ORDER_STATUS_DICT['주문 완료']][0])

    @classmethod
    def pushOrder(cls, userInstance, storeInstance, menuInstance, pickupTime):
        orderDate             = dateNowByTimeZone()
        orderDateWithoutTime  = orderDate.replace(hour=0, minute=0, second=0, microsecond=0)

        pickupTime            = cls.rowPickupTimeToDatetime(pickupTime)

        # Next Lunch Order Edit Time 16:30 ~ 9:30(~ 10:30)
        nextlunchOrderEditTimeStart   = orderDateWithoutTime + timedelta(hours=16, minutes=30)
        nextlunchOrderTimeEnd         = orderDateWithoutTime + timedelta(hours=10, minutes=30, days=1)

        if(nextlunchOrderEditTimeStart <= orderDate) and (orderDate <= nextlunchOrderTimeEnd):
            pickupTime = pickupTime + timedelta(days=1)

        managementCode  = OrderManagementCodeGenerator(storeInstance, menuInstance, userInstance, orderDate)

        pushedOrder = cls(userInstance=userInstance, storeInstance=storeInstance, menuInstance=menuInstance, management_code=managementCode, pickupTime=pickupTime, order_date=orderDate)
        pushedOrder.save()

        return pushedOrder

    @staticmethod
    def rowPickupTimeToDatetime(rowPickupTime):
        return dateNowByTimeZone().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(hours=int(rowPickupTime[0:2]), minutes=int(rowPickupTime[3:5]))

    # Methods
    def __str__(self):
        return "{} - {} :: {}".format(self.management_code, self.status, self.order_date)

class OrderManager():
    def __init__(self, userID):
        self.userOrderList = Order.objects.filter(userInstance__id=userID)

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
        lunchCoupons     = availableCoupons.filter(menuInstance__sellingTime=SELLING_TIME_CATEGORY[SELLING_TIME_LUNCH][0])
        return lunchCoupons

    def getAvailableDinnerCouponPurchased(self):
        availableCoupons = self.getAvailableCoupons()
        dinnerCoupons    = availableCoupons.filter(menuInstance__sellingTime=SELLING_TIME_CATEGORY[SELLING_TIME_DINNER][0])
        return dinnerCoupons