# Define
from eatple_app.define import *

from eatple_app.apis.slack.slack_logger import SlackLogPayOrder, SlackLogCancelOrder, SlackLogUsedOrder

# Django Library
from django.urls import reverse
from django.db import models
from django.db.models import Q
from django_mysql.models import Model

from eatple_app.model.orderRecord import OrderRecordSheet, OrderRecord

from eatple_app.module_kakao.kakaoPay import *
from eatple_app.module_iamport.iamport import *

FRIEND_DISCOUNT = 2000


def iamportOrderValidation(order):
    iamport = Iamport()
    try:
        response = iamport.find(merchant_uid=order.order_id)
    except KeyError:
        return order

    except Iamport.ResponseError as e:
        order.payment_status = EATPLE_ORDER_STATUS_FAILED
        order.save()

        return order

    except Iamport.HttpError as http_error:
        if(order.payment_status != EATPLE_ORDER_STATUS_FAILED):
            order.payment_status = EATPLE_ORDER_STATUS_NOT_PUSHED
            order.save()

        return order

    order.payment_status = response['status']
    order.save()

    return order


def iamportOrderCancel(order, description='주문취소'):
    iamport = Iamport()

    try:
        response = iamport.cancel(description, merchant_uid=order.order_id)
    except (KeyError, Iamport.ResponseError):
        return False

    except Iamport.HttpError as http_error:
        return False

    return True


def kakaoPayOrderValidation(order):
    try:
        response = KakaoPay().OrderStatus(tid=order.order_kakaopay.tid)
    except Order.order_kakaopay.RelatedObjectDoesNotExist as ex:
        if(order.payment_status != EATPLE_ORDER_STATUS_FAILED):
            order.payment_status = EATPLE_ORDER_STATUS_NOT_PUSHED
            order.save()
        else:
            order.payment_status = EATPLE_ORDER_STATUS_FAILED
            order.save()

        return order

    kakaoPayStatus = json.loads(response.text)['status']
    print("카카오 주문 상태 : ", kakaoPayStatus)
    if(
        kakaoPayStatus == 'READY' or
        kakaoPayStatus == 'SEND_TMS' or
        kakaoPayStatus == 'OPEN_PAYMENT' or
        kakaoPayStatus == 'SELECT_METHOD' or
        kakaoPayStatus == 'ARS_WAITING' or
        kakaoPayStatus == 'AUTH_PASSWORD' or
        kakaoPayStatus == 'FAIL_AUTH_PASSWORD'
    ):
        if(order.payment_status != EATPLE_ORDER_STATUS_FAILED):
            order.payment_status = EATPLE_ORDER_STATUS_NOT_PUSHED

    elif(kakaoPayStatus == 'SUCCESS_PAYMENT'):
        order.payment_status = EATPLE_ORDER_STATUS_PAID
    elif(
        kakaoPayStatus == 'CANCEL_PAYMENT' or
        kakaoPayStatus == 'PART_CANCEL_PAYMENT'
    ):
        order.payment_status = EATPLE_ORDER_STATUS_CANCELLED
    elif(
        kakaoPayStatus == 'QUIT_PAYMENT' or
        kakaoPayStatus == 'FAIL_PAYMENT'
    ):
        order.payment_status = EATPLE_ORDER_STATUS_FAILED
    else:
        order.payment_status = EATPLE_ORDER_STATUS_FAILED

    order.save()

    return order


def kakaoPayOrderCancel(order):
    try:
        response = KakaoPay().OrderCancel(
            tid=order.order_kakaopay.tid,
            cancel_amount=order.totalPrice,
            cancel_tax_free_amount=0,
        )
        return True
    except Order.order_kakaopay.RelatedObjectDoesNotExist as ex:
        order.payment_status = EATPLE_ORDER_STATUS_FAILED
        order.save()

        return False

    return False


def eatplePayPassOrderCancel(order):
    order.payment_status = EATPLE_ORDER_STATUS_CANCELLED
    order.save()

    return True


def orderUpdate(order):
    print('주문 상태 =>')

    # Normal User Pass
    if(order.menu == None or order.store == None):
        order.payment_status = EATPLE_ORDER_STATUS_NOT_PUSHED
    else:
        if(order.payment_type == ORDER_PAYMENT_INI_PAY):
            order = iamportOrderValidation(order)
        elif(order.payment_type == ORDER_PAYMENT_KAKAO_PAY):
            order = kakaoPayOrderValidation(order)
        elif(order.payment_type == ORDER_PAYMENT_PAY_PASS):
            order.payment_status = order.payment_status
        else:
            order.payment_status = order.payment_status

        if(order.payment_status == EATPLE_ORDER_STATUS_FAILED and
                order.order_date >= dateNowByTimeZone() - datetime.timedelta(minutes=30)):
            order.payment_status = EATPLE_ORDER_STATUS_NOT_PUSHED

    order.save()

    # Payment State Update
    if(order.payment_status == EATPLE_ORDER_STATUS_CANCELLED):
        # @PROMOTION
        if(order.type == ORDER_TYPE_PROMOTION):
            order.ordersheet.user.cancelPromotion()

        order.status = ORDER_STATUS_ORDER_CANCELED
        order.save()
        print('주문 취소됨')

    if(order.payment_status == EATPLE_ORDER_STATUS_READY):
        order.status = ORDER_STATUS_MENU_CHOCIED
        order.save()
        print('주문 미결제 또는 진행중')

    if(order.payment_status == EATPLE_ORDER_STATUS_FAILED):
        order.status = ORDER_STATUS_ORDER_FAILED
        order.save()
        print('주문 실패')

    if(order.payment_status == EATPLE_ORDER_STATUS_NOT_PUSHED):
        order.status = ORDER_STATUS_MENU_CHOCIED
        order.save()
        print('메뉴 선택중')

    if(order.payment_status == EATPLE_ORDER_STATUS_PAID):
        print(order.status, ORDER_STATUS_MENU_CHOCIED)
        if(order.status == ORDER_STATUS_MENU_CHOCIED or order.status == ORDER_STATUS_ORDER_CONFIRM_WAIT):
            order.status = ORDER_STATUS_ORDER_CONFIRMED
            order.save()

            order.orderPay()
            print('주문 결제됨')

        # @PROMOTION
        if(order.type == ORDER_TYPE_PROMOTION):
            order.ordersheet.user.applyPromotion()
            print('주문 결제됨')

    if(order.payment_status != EATPLE_ORDER_STATUS_PAID):
        return order

    if(order.status == ORDER_STATUS_PICKUP_COMPLETED or order.status == ORDER_STATUS_ORDER_EXPIRED):
        return order

    # Ordering State Update
    menu = order.menu

    paymentDate = order.payment_date
    paymentDateWithoutTime = paymentDate.replace(
        hour=0, minute=0, second=0, microsecond=0)

    orderTimeSheet = OrderTimeSheet()

    currentDate = orderTimeSheet.GetCurrentDate()
    currentDateWithoutTime = orderTimeSheet.GetCurrentDateWithoutTime()

    YESTERDAY = orderTimeSheet.GetYesterDay()
    TODAY = orderTimeSheet.GetToday()
    TOMORROW = orderTimeSheet.GetTomorrow()

    PICKUP_DAY = dateByTimeZone(order.pickup_time).replace(
        hour=0, minute=0, second=0, microsecond=0)
    PICKUP_YESTER_DAY = PICKUP_DAY + datetime.timedelta(days=-1)

    prevLunchOrderEditTimeStart = orderTimeSheet.GetPrevLunchOrderEditTimeStart()
    prevLunchOrderEditTimeEnd = orderTimeSheet.GetPrevLunchOrderEditTimeEnd()
    prevLunchOrderTimeEnd = orderTimeSheet.GetPrevLunchOrderTimeEnd()

    # Dinner Order Edit Time
    dinnerOrderEditTimeStart = orderTimeSheet.GetDinnerOrderEditTimeStart()
    dinnerOrderEditTimeEnd = orderTimeSheet.GetDinnerOrderEditTimeEnd()
    dinnerOrderTimeEnd = orderTimeSheet.GetDinnerOrderTimeEnd()

    # Next Lunch Order Edit Time
    nextLunchOrderEditTimeStart = orderTimeSheet.GetNextLunchOrderEditTimeStart()
    nextLunchOrderEditTimeEnd = orderTimeSheet.GetNextLunchOrderEditTimeEnd()
    nextLunchOrderTimeEnd = orderTimeSheet.GetNextLunchOrderTimeEnd()

    # Lunch Order Pickup Time
    lunchOrderPickupTimeStart = orderTimeSheet.GetLunchOrderPickupTimeStart()
    lunchOrderPickupTimeEnd = orderTimeSheet.GetLunchOrderPickupTimeEnd()

    # Dinner Order Pickup Time
    dinnerOrderPickupTimeStart = orderTimeSheet.GetDinnerOrderPickupTimeStart()
    dinnerOrderPickupTimeEnd = orderTimeSheet.GetDinnerOrderPickupTimeEnd()

    print(menu.selling_time)
    print(paymentDate)
    print((paymentDateWithoutTime == TODAY), paymentDateWithoutTime, TODAY, )
    # Lunch Order
    if (SELLING_TIME_LUNCH == menu.selling_time) and \
        ((PICKUP_YESTER_DAY <= paymentDateWithoutTime) and
            (TODAY <= PICKUP_DAY)):

        # Pickup Prepare Time
        if(prevLunchOrderTimeEnd <= currentDate) and (currentDate < lunchOrderPickupTimeStart) and \
                (TODAY == PICKUP_DAY):
            print("픽업 준비중 - A")
            order.status = ORDER_STATUS_PICKUP_PREPARE
        # PickupTime Waiting Time
        elif(lunchOrderPickupTimeStart <= currentDate) and (currentDate < lunchOrderPickupTimeEnd) and \
                (TODAY == PICKUP_DAY):
            # Over Order Pickup Time
            if(order.pickup_time + datetime.timedelta(minutes=-15) <= currentDate):
                print("픽업 대기중 - A")
                order.status = ORDER_STATUS_PICKUP_WAIT
            else:
                print("픽업 준비중 - B")
                order.status = ORDER_STATUS_PICKUP_PREPARE
        # Order Time Range
        else:
            # prev phase Order
            if(prevLunchOrderEditTimeStart <= currentDate) and (currentDate < prevLunchOrderTimeEnd):
                if currentDate <= prevLunchOrderEditTimeEnd:
                    print("주문 완료 - A")
                    order.status = ORDER_STATUS_ORDER_CONFIRMED
                else:
                    print("픽업 준비중 - C")
                    order.status = ORDER_STATUS_PICKUP_PREPARE

            # next phase Lunch order
            elif (nextLunchOrderEditTimeStart <= currentDate) and \
                 (currentDate < nextLunchOrderEditTimeEnd) and \
                 (nextLunchOrderEditTimeStart <= paymentDate):
                print("주문 완료 - B")
                order.status = ORDER_STATUS_ORDER_CONFIRMED

            elif (prevLunchOrderTimeEnd <= currentDate) and \
                    (currentDate < nextLunchOrderEditTimeStart):
                if currentDate < lunchOrderPickupTimeEnd:
                    print("주문 완료 - C")
                    order.status = ORDER_STATUS_ORDER_CONFIRMED
                else:
                    print("픽업 완료 - A")
                    order.status = ORDER_STATUS_PICKUP_COMPLETED

            # Invalid Time Range is Dinner Order Time ( prev phase lunch order ~ dinner order ~ next phase lunch order )
            else:
                print("픽업 완료 - ERROR")
                order.status = ORDER_STATUS_PICKUP_COMPLETED

    # Dinner Order
    elif ((SELLING_TIME_DINNER == menu.selling_time) and (paymentDateWithoutTime == TODAY)):
        # Meal Pre-
        if(dinnerOrderTimeEnd <= currentDate) and (currentDate < dinnerOrderPickupTimeStart):
            print("픽업 준비중 - A")
            order.status = ORDER_STATUS_PICKUP_PREPARE
        # PickupTime Range
        elif(dinnerOrderPickupTimeStart <= currentDate) and (currentDate < dinnerOrderPickupTimeEnd):
            # Over Order Pickup Time
            if(order.pickup_time + datetime.timedelta(minutes=-15) <= currentDate):
                print("픽업 대기중 - A")
                order.status = ORDER_STATUS_PICKUP_WAIT
            else:
                print("픽업 준비중 - B")
                order.status = ORDER_STATUS_PICKUP_PREPARE

        else:
            # Today Order
            if(dinnerOrderEditTimeStart <= currentDate) and (currentDate <= dinnerOrderTimeEnd):
                if currentDate <= dinnerOrderEditTimeEnd:
                    print("주문 완료 - A")
                    order.status = ORDER_STATUS_ORDER_CONFIRMED
                else:
                    print("픽업 준비중 - C")
                    order.status = ORDER_STATUS_PICKUP_PREPARE

            # Invalid Time Range is Lunch Order Time ( prev phase lunch order ~ dinner order ~ next phase lunch order )
            else:
                print("픽업 완료 - ERROR")
                order.status = ORDER_STATUS_PICKUP_COMPLETED

    # Invalid Order Selling Time
    else:
        print("주문 만료 - A")
        order.status = ORDER_STATUS_ORDER_EXPIRED

    order.save()
    return order


class Order_KakaoPay(models.Model):
    class Meta:
        verbose_name = "카카오 페이"
        verbose_name_plural = "카카오 페이"

        ordering = ['-tid']

    order = models.OneToOneField(
        'Order',
        on_delete=models.CASCADE,
        null=True,
        verbose_name="주문서"
    )

    tid = models.CharField(
        max_length=MANAGEMENT_CODE_LENGTH,
        blank=True,
        null=True,
        verbose_name="고유 주문 번호( TID )"
    )

    pg_token = models.CharField(
        max_length=MANAGEMENT_CODE_LENGTH,
        blank=True,
        null=True,
        verbose_name="PG사 주문별 토큰"
    )

    def approve(self, tid, pg_token=None):
        self.tid = tid
        self.pg_token = pg_token
        self.save()

        return self.order


class Order(models.Model):
    class Meta:
        verbose_name = "주문 내역"
        verbose_name_plural = "주문 내역"

        ordering = ['-order_date']

    order_id = models.CharField(
        max_length=MANAGEMENT_CODE_LENGTH,
        blank=True,
        null=True,
        verbose_name="주문 번호"
    )

    ordersheet = models.ForeignKey(
        'OrderSheet',
        on_delete=models.CASCADE,
        null=True,
        verbose_name="주문시트 번호"
    )

    store = models.ForeignKey(
        'Store',
        on_delete=models.CASCADE,
        null=True,
        verbose_name="상점"
    )

    menu = models.ForeignKey(
        'Menu',
        on_delete=models.CASCADE,
        null=True,
        verbose_name="메뉴"
    )

    totalPrice = models.IntegerField(
        default=0,
        verbose_name="총 금액"
    )

    discount = models.IntegerField(
        default=0,
        verbose_name="할인액"
    )

    count = models.IntegerField(
        default=1,
        verbose_name="주문 개수"
    )

    pickup_time = models.DateTimeField(
        default=timezone.now,
        verbose_name="픽업 시간"
    )

    payment_status = models.CharField(
        max_length=10,
        choices=EATPLE_ORDER_STATUS,
        default=EATPLE_ORDER_STATUS_NOT_PUSHED,
        verbose_name="결제 상태"
    )

    status = models.IntegerField(
        choices=ORDER_STATUS,
        default=ORDER_STATUS_MENU_CHOCIED,
        verbose_name="주문 상태"
    )

    type = models.CharField(
        max_length=WORD_LENGTH,
        default=ORDER_TYPE_NORMAL,
        choices=ORDER_TYPE,
        verbose_name="주문 타입"
    )

    payment_type = models.CharField(
        max_length=WORD_LENGTH,
        default=ORDER_PAYMENT_INI_PAY,
        choices=ORDER_PAYMENT_TYPE,
        verbose_name="결제 타입"
    )

    delegate = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="위임자"
    )

    update_date = models.DateTimeField(
        auto_now=True,
        verbose_name="마지막 수정일"
    )

    order_date = models.DateTimeField(
        default=timezone.now,
        verbose_name="주문 시간"
    )

    payment_date = models.DateTimeField(
        default=timezone.now,
        verbose_name="결제 완료 시간"
    )

    pickup_complete_date = models.DateTimeField(
        default=timezone.now,
        verbose_name="픽업 완료 시간"
    )

    def save(self, *args, **kwargs):
        super().save()

    @staticmethod
    def pickupTimeToDateTime(pickup_time):
        pickup_time = [x.strip() for x in pickup_time.split(':')]

        currentTime = dateNowByTimeZone()
        datetime_pickup_time = currentTime.replace(
            hour=int(pickup_time[0]),
            minute=int(pickup_time[1]),
            second=0,
            microsecond=0
        )

        if(datetime_pickup_time < currentTime):
            datetime_pickup_time += datetime.timedelta(days=1)

        return datetime_pickup_time

    def orderStatusUpdate(self):
        return orderUpdate(self)

    def orderPay(self):
        self.payment_status = EATPLE_ORDER_STATUS_PAID
        self.payment_date = dateNowByTimeZone()

        if(self.payment_type == ORDER_PAYMENT_PAY_PASS):
            self.status = ORDER_STATUS_ORDER_CONFIRMED

        if(self.ordersheet.user.friend_discount_count > 0):
            self.ordersheet.user.use_friend_discount()

        self.save()

        # @SLACK LOGGER
        SlackLogPayOrder(self)

        return self

    def orderCancel(self):
        isCancelled = False

        if(self.payment_type == ORDER_PAYMENT_INI_PAY):
            isCancelled = iamportOrderCancel(self)
        elif(self.payment_type == ORDER_PAYMENT_KAKAO_PAY):
            isCancelled = kakaoPayOrderCancel(self)
        elif(self.payment_type == ORDER_PAYMENT_PAY_PASS):
            isCancelled = eatplePayPassOrderCancel(self)
        else:
            isCancelled = False

        if(isCancelled):
            if((self.menu.price - self.totalPrice) >= FRIEND_DISCOUNT):
                self.ordersheet.user.cancel_friend_discount()

            # Order Record
            try:
                orderRecordSheet = OrderRecordSheet.objects.get(order=self)
            except OrderRecordSheet.DoesNotExist:
                orderRecordSheet = OrderRecordSheet()

            orderRecordSheet.user = self.ordersheet.user
            orderRecordSheet.order = self
            orderRecordSheet.paid = True
            orderRecordSheet.recordUpdate(
                orderRecordSheet.user, orderRecordSheet.order, ORDER_RECORD_PAYMENT_CANCELED)

            # @SLACK LOGGER
            SlackLogCancelOrder(self)

        return isCancelled

    def orderUsed(self):
        self.status = ORDER_STATUS_PICKUP_COMPLETED
        self.pickup_complete_date = dateNowByTimeZone()
        self.save()

        # Order Record
        try:
            orderRecordSheet = OrderRecordSheet.objects.get(order=self)
        except OrderRecordSheet.DoesNotExist:
            orderRecordSheet = OrderRecordSheet()

        orderRecordSheet.user = self.ordersheet.user
        orderRecordSheet.order = self
        orderRecordSheet.paid = True
        orderRecordSheet.recordUpdate(
            orderRecordSheet.user, orderRecordSheet.order, ORDER_RECORD_PAYMENT_COMPLETED)

        # @SLACK LOGGER
        SlackLogUsedOrder(self)

        return self

    def orderDelegate(self, order):
        if(self.delegate != None):
            return None

        if(self.store == order.store and
           self.pickup_time == order.pickup_time):

            self.delegate = order.ordersheet.user
            self.save()

        return self

    def orderDelegateCancel(self):
        self.delegate = None
        self.save()

        return self

    # Methods
    def __str__(self):
        return '{}'.format(self.order_id)


class OrderManager():
    def __init__(self, user):
        self.orderList = Order.objects.all()

    def availableOrderStatusUpdate(self):
        availableOrders = self.getAvailableOrders()

        # Order Status Update
        for order in availableOrders:
            orderUpdate(order)

        return self.getAvailableOrders()

    def orderPenddingCleanUp(self):
        orderTimeSheet = OrderTimeSheet()
        currentDate = orderTimeSheet.GetCurrentDate()
        expireDate = orderTimeSheet.GetOrderExpireDate()

        readyPayOrders = Order.objects.filter(
            Q(payment_status=EATPLE_ORDER_STATUS_NOT_PUSHED) &
            Q(payment_date__gte=expireDate) &
            ~Q(store=None) &
            ~Q(menu=None)
        ).order_by('order_date')

        # Order Status Update
        for order in readyPayOrders:
            orderUpdate(order)
            if(order.payment_status != EATPLE_ORDER_STATUS_PAID):
                order.payment_status = EATPLE_ORDER_STATUS_FAILED
                order.status = ORDER_STATUS_MENU_CHOCIED
                order.save()

    def orderPaidCheck(self):
        orderTimeSheet = OrderTimeSheet()
        currentDate = orderTimeSheet.GetCurrentDate()
        expireDate = orderTimeSheet.GetOrderExpireDate()

        readyPayOrders = Order.objects.filter(
            Q(payment_status=EATPLE_ORDER_STATUS_NOT_PUSHED) &
            Q(payment_date__gte=expireDate) &
            ~Q(store=None) &
            ~Q(menu=None)
        ).order_by('order_date')

        # Order Status Update
        for order in readyPayOrders:
            orderUpdate(order)

    def getUnavailableOrders(self):
        unavailableOrders = self.orderList.filter(
            Q(status=ORDER_STATUS_ORDER_EXPIRED) |
            Q(status=ORDER_STATUS_ORDER_CANCELED) |
            Q(status=ORDER_STATUS_PAYMENT_CHECK) |
            Q(status=ORDER_STATUS_PICKUP_COMPLETED)
        )

        return unavailableOrders

    def getAvailableOrders(self):
        orderTimeSheet = OrderTimeSheet()
        currentDate = orderTimeSheet.GetCurrentDate()
        expireDate = orderTimeSheet.GetOrderExpireDate()

        availableOrders = self.orderList.filter(
            (
                Q(status=ORDER_STATUS_PICKUP_WAIT) |
                Q(status=ORDER_STATUS_PICKUP_PREPARE) |
                Q(status=ORDER_STATUS_ORDER_CONFIRM_WAIT) |
                Q(status=ORDER_STATUS_ORDER_CONFIRMED)
            ) &
            Q(payment_date__gte=expireDate)
        )

        return availableOrders

    def getAvailableLunchOrder(self):
        availableOrders = self.getAvailableOrders()
        lunchOrders = availableOrders.filter(
            menu__selling_time=SELLING_TIME_LUNCH
        )

        return lunchOrders

    def getAvailableDinnerOrder(self):
        availableOrders = self.getAvailableOrders()
        dinnerOrders = availableOrders.filter(
            menu__selling_time=SELLING_TIME_DINNER
        )

        return dinnerOrders


class UserOrderManager(OrderManager):
    def __init__(self, user, selling_time=None):
        self.orderList = Order.objects.filter(
            Q(ordersheet__user=user) |
            Q(delegate=user)
        )

        if(selling_time != None):
            self.orderList = self.orderList.filter(
                menu__selling_time=selling_time)


class PartnerOrderManager(OrderManager):
    def __init__(self, partner, selling_time=None):
        self.orderList = Order.objects.filter(store=partner.store)

        if(selling_time != None):
            self.orderList = self.orderList.filter(
                menu__selling_time=selling_time)


class OrderSheet(models.Model):
    class Meta:
        verbose_name = "주문 내역 시트"
        verbose_name_plural = "주문 내역 시트"

        ordering = ['-create_date']

    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        null=True,
        verbose_name="소유자"
    )

    management_code = models.CharField(
        max_length=MANAGEMENT_CODE_LENGTH,
        blank=True,
        null=True,
        verbose_name="주문시트 관리번호"
    )

    update_date = models.DateTimeField(
        auto_now=True,
        verbose_name="마지막 수정일"
    )
    create_date = models.DateTimeField(
        default=timezone.now,
        verbose_name="생성일자"
    )

    def __init__(self, *args, **kwargs):
        super(OrderSheet, self).__init__(*args, **kwargs)

        if (self.id == None):
            try:
                self.id = OrderSheet.objects.latest('id').id + 1
            except (OrderSheet.DoesNotExist) as ex:
                self.id = 1

        if(self.create_date == None):
            self.create_date = datetime.datetime.now()

        self.management_code = 'E{area:06X}P{id:03X}'.format(
            area=int(self.create_date.strftime('%f')), id=self.id)

    def save(self, *args, **kwargs):
        super().save()

    def pushOrder(self, user, store, menu, pickup_time, totalPrice, count, type):
        self.user = user
        super().save()

        try:
            order_id = Order.objects.latest('id').id + 1
        except (Order.DoesNotExist) as ex:
            order_id = 1

        order_id = 'EP{area:08X}{id:04X}'.format(
            area=int(datetime.datetime.now().strftime('%f')), id=self.id)

        order = Order()
        order.ordersheet = self
        order.order_id = order_id
        order.menu = menu
        order.store = store

        order.pickup_time = order.pickupTimeToDateTime(pickup_time)

        order.totalPrice = totalPrice
        order.count = count
        order.type = type
        order.save()

        return order

    # Methods
    def __str__(self):
        return '{}'.format(self.management_code)
