# Django Library
from django.urls import reverse
from django.db import models
from django.db.models import Q
from django_mysql.models import Model

# Define
from eatple_app.define import *


def iamportOrderValidation(order):
    iamport = Iamport(imp_key=IAMPORT_API_KEY,
                      imp_secret=IAMPORT_API_SECRET_KEY)
    try:
        response = iamport.find(merchant_uid=order.order_id)
    except (KeyError, Iamport.ResponseError, Iamport.HttpError):
        order.payment_status = IAMPORT_ORDER_STATUS_READY
        order.status = ORDER_STATUS_PAYMENT_CHECK
        order.save()

        return IAMPORT_ORDER_STATUS_READY


    if(response['status'] == IAMPORT_ORDER_STATUS_PAID and
            order.payment_status == IAMPORT_ORDER_STATUS_READY):
        order.payment_status = IAMPORT_ORDER_STATUS_PAID
        order.status = ORDER_STATUS_ORDER_CONFIRM_WAIT
        order.save()

    return order.status


def orderUpdate(order):
    status = iamportOrderValidation(order)

    if(status == ORDER_STATUS_ORDER_FAILED):
        return status

    menu = order.menu

    orderDate = dateByTimeZone(order.order_date)
    orderDateWithoutTime = orderDate.replace(
        hour=0, minute=0, second=0, microsecond=0)

    currentDate = dateNowByTimeZone()
    currentDateWithoutTime = currentDate.replace(
        hour=0, minute=0, second=0, microsecond=0)

    YESTERDAY = currentDateWithoutTime + \
        datetime.timedelta(days=-1)  # Yesterday start
    TODAY = currentDateWithoutTime
    TOMORROW = currentDateWithoutTime + \
        datetime.timedelta(days=1)  # Tommorrow start

    # Prev Lunch Order Edit Time 16:30 ~ 9:30(~ 10:30)
    prevlunchOrderEditTimeStart = currentDateWithoutTime + \
        datetime.timedelta(hours=16, minutes=30, days=-1)
    prevlunchOrderEditTimeEnd = currentDateWithoutTime + \
        datetime.timedelta(hours=9, minutes=30)
    prevlunchOrderTimeEnd = currentDateWithoutTime + \
        datetime.timedelta(hours=10, minutes=30)

    # Dinner Order Edit Time 11:30 ~ 15:30(~ 16:30)
    dinnerOrderEditTimeStart = currentDateWithoutTime + \
        datetime.timedelta(hours=11, minutes=30)
    dinnerOrderEditTimeEnd = currentDateWithoutTime + \
        datetime.timedelta(hours=15, minutes=30)
    dinnerOrderTimeEnd = currentDateWithoutTime + \
        datetime.timedelta(hours=16, minutes=30)

    # Next Lunch Order Edit Time 16:30 ~ 9:30(~ 10:30)
    nextlunchOrderEditTimeStart = currentDateWithoutTime + \
        datetime.timedelta(hours=16, minutes=30)
    nextlunchOrderEditTimeEnd = currentDateWithoutTime + \
        datetime.timedelta(hours=9, minutes=30, days=1)
    nextlunchOrderTimeEnd = currentDateWithoutTime + \
        datetime.timedelta(hours=10, minutes=30, days=1)

    # Lunch Order Pickup Time (10:30 ~)11:30 ~ 13:30
    lunchOrderPickupTimeStart = currentDateWithoutTime + \
        datetime.timedelta(hours=11, minutes=30)
    lunchOrderPickupTimeEnd = currentDateWithoutTime + \
        datetime.timedelta(hours=13, minutes=30)

    # Dinner Order Pickup Time (16:30 ~)17:30 ~ 21:00
    dinnerOrderPickupTimeStart = currentDateWithoutTime + \
        datetime.timedelta(hours=17, minutes=30)
    dinnerOrderPickupTimeEnd = currentDateWithoutTime + \
        datetime.timedelta(hours=21, minutes=0)

    # Lunch Order
    if (SELLING_TIME_LUNCH == menu.sellingTime) and \
            ((YESTERDAY <= orderDateWithoutTime) and (orderDateWithoutTime <= TODAY)):

        # Meal Pre-
        if(prevlunchOrderTimeEnd <= currentDate) and (currentDate <= lunchOrderPickupTimeStart):
            order.status = ORDER_STATUS_PICKUP_PREPARE
            order.save()
        # PickupTime Range
        elif(lunchOrderPickupTimeStart <= currentDate) and (currentDate <= lunchOrderPickupTimeEnd):
            # Over Order Pickup Time
            if(currentDate >= orderPickupTime):
                order.status = ORDER_STATUS_PICKUP_WAIT
                order.save()
            else:
                order.status = ORDER_STATUS_PICKUP_PREPARE
                order.save()
        # Order Time Range
        else:
            # prev phase Order
            if(prevlunchOrderEditTimeStart <= currentDate) and (currentDate <= prevlunchOrderTimeEnd):
                if currentDate <= prevlunchOrderEditTimeEnd:
                    order.status = ORDER_STATUS_ORDER_CONFIRMED
                    order.save()

                else:
                    order.status = ORDER_STATUS_PICKUP_PREPARE
                    order.save()

            # next phase Lunch order
            elif (nextlunchOrderTimeEnd >= currentDate) and (orderDateWithoutTime >= TODAY):
                order.status = ORDER_STATUS_ORDER_CONFIRMED
                order.save()

            # Invalid Time Range is Dinner Order Time ( prev phase lunch order ~ dinner order ~ next phase lunch order )
            else:
                order.status = ORDER_STATUS_ORDER_EXPIRED
                order.save()

    # Dinner Order
    elif (SELLING_TIME_DINNER == menu.sellingTime) and (orderDateWithoutTime == TODAY):
        # Meal Pre-
        if(dinnerOrderTimeEnd <= currentDate) and (currentDate <= dinnerOrderPickupTimeStart):
            order.status = ORDER_STATUS_PICKUP_PREPARE
            order.save()
        # PickupTime Range
        elif(dinnerOrderPickupTimeStart <= currentDate) and (currentDate <= dinnerOrderPickupTimeEnd):
            # Over Order Pickup Time
            if(currentDate >= orderPickupTime):
                order.status = ORDER_STATUS_PICKUP_WAIT
                order.save()
            else:
                order.status = ORDER_STATUS_PICKUP_PREPARE
                order.save()
        else:
            # Today Order
            if(dinnerOrderEditTimeStart < currentDate) and (currentDate < dinnerOrderTimeEnd):

                if orderDate <= dinnerOrderEditTimeEnd:
                    order.status = ORDER_STATUS_ORDER_CONFIRMED
                    order.save()

                else:
                    order.status = ORDER_STATUS_PICKUP_PREPARE
                    order.save()
            # Invalid Time Range is Lunch Order Time ( prev phase lunch order ~ dinner order ~ next phase lunch order )
            else:
                order.status = ORDER_STATUS_ORDER_EXPIRED
                order.save()

    # Invalid Order Selling Time
    else:
        order.status = ORDER_STATUS_ORDER_EXPIRED
        order.save()

    return order.status


class Order(models.Model):
    class Meta:
        ordering = ['-pickup_time']

    order_id = models.CharField(
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

    totalPrice = models.IntegerField(default=0)

    count = models.IntegerField(default=1)

    pickup_time = models.DateTimeField(default=timezone.now)

    payment_status = models.CharField(
        max_length=10,
        choices=IAMPORT_ORDER_STATUS,
        default=IAMPORT_ORDER_STATUS_READY
    )

    status = models.IntegerField(
        choices=ORDER_STATUS,
        default=ORDER_STATUS_PAYMENT_CHECK,
    )

    update_date = models.DateTimeField(auto_now=True)
    order_date = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        super().save()

    @staticmethod
    def pickupTimeToDateTime(pickup_time):
        pickup_time = [x.strip() for x in pickup_time.split(':')]

        currentTime = dateByTimeZone(timezone.now())
        datetime_pickup_time = currentTime.replace(
                                    hour=int(pickup_time[0]), 
                                    minute=int(pickup_time[1]),
                                    second=0,
                                    microsecond=0
                                    )

        if(datetime_pickup_time < currentTime):
            datetime_pickup_time += datetime.timedelta(days=1)
            
        print(datetime_pickup_time)
        
        return datetime_pickup_time

    def __init__(self, *args, **kwargs):
        super(Order, self).__init__(*args, **kwargs)

        if (self.id == None):
            try:
                self.id = Order.objects.latest('id').id + 1
            except (Order.DoesNotExist) as ex:
                self.id = 1

        if(self.order_date == None):
            self.order_date = datetime.datetime.now()

        self.order_id = "EP{area:08X}{id:04X}".format(
            area=int(self.order_date.strftime('%f')), id=self.id)

    # Methods
    def __str__(self):
        return "{}".format(self.order_id)

class OrderManager():
    def __init__(self, user):
        self.userOrderList = Order.objects.filter(
            ordersheet__user=user)

    def orderStatusUpdate(self, order):
        return orderUpdate(order)

    def availableOrderStatusUpdate(self):
        availableOrders = self.getAvailableOrders()

        # Order Status Update
        for order in availableOrders:
            orderUpdate(order)

        return self.getAvailableOrders()

    def orderPaidCheck(self):
        readyPayOrders = Order.objects.filter(
            Q(payment_status=IAMPORT_ORDER_STATUS_READY)
        )

        # Order Status Update
        for order in readyPayOrders:
            orderUpdate(order)

    def getUnavailableOrders(self):
        unavailableOrders = self.userOrderList.filter(
            Q(status=ORDER_STATUS_ORDER_EXPIRED) |
            Q(status=ORDER_STATUS_ORDER_CANCELED) |
            Q(status=ORDER_STATUS_PAYMENT_CHECK) |
            Q(status=ORDER_STATUS_PICKUP_COMPLETED)
        )

        return unavailableOrders

    def getAvailableOrders(self):
        availableOrders = self.userOrderList.filter(
            Q(status=ORDER_STATUS_PICKUP_WAIT) |
            Q(status=ORDER_STATUS_PICKUP_PREPARE) |
            Q(status=ORDER_STATUS_ORDER_CONFIRM_WAIT) |
            Q(status=ORDER_STATUS_ORDER_CONFIRMED)
        )

        return availableOrders

    def getAvailableLunchuserOrderListPurchased(self):
        availableOrders = self.getAvailableOrders()
        lunchOrders = availableOrders.filter(
            menu__sellingTime=SELLING_TIME_LUNCH)

        return lunchOrders

    def getAvailableDinnerOrderPurchased(self):
        availableOrders = self.getAvailableOrders()
        dinnerOrders = availableOrders.filter(
            menu__sellingTime=SELLING_TIME_DINNER)
        return dinnerOrders


class storeOrderManager(OrderManager):
    def __init__(self, storeId):
        self.storeOrderList = Order.objects.filter(storeInstance__id=storeId)


class OrderSheet(models.Model):
    class Meta:
        ordering = ['-create_date']

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
    create_date = models.DateTimeField(default=timezone.now)

    def __init__(self, *args, **kwargs):
        super(OrderSheet, self).__init__(*args, **kwargs)

        if (self.id == None):
            try:
                self.id = OrderSheet.objects.latest('id').id + 1
            except (OrderSheet.DoesNotExist) as ex:
                self.id = 1

        if(self.create_date == None):
            self.create_date = datetime.datetime.now()

        self.management_code = "E{area:06X}P{id:03X}".format(
            area=int(self.create_date.strftime('%f')), id=self.id)

    def save(self, *args, **kwargs):
        super().save()

    def pushOrder(self, user, store, menu, pickup_time, totalPrice, count):
        self.user = user
        super().save()

        order = Order()
        order.ordersheet = self
        order.menu = menu
        order.store = store
        order.pickup_time = order.pickupTimeToDateTime(pickup_time)
        order.totalPrice = totalPrice
        order.count = 1
        order.save()

        return order

    # Methods
    def __str__(self):
        return "{}".format(self.management_code)
