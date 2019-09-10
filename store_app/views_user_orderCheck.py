#Django Library
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils import timezone

#External Library
import requests
import json
import sys
import pytz
from datetime import datetime, timedelta

#Models 
from .models_config import Config

from .models_user  import User
from .models_order import Order
from .models_store import Store, Menu, Category, SubCategory

#View Modules
from .module_KakaoForm import Kakao_SimpleForm, Kakao_CarouselForm

#View
from .views_kakaoTool import getLatLng, KakaoPayLoad
from .views_system import EatplusSkillLog, errorView

#GLOBAL CONFIG
TIME_ZONE                   = Config.TIME_ZONE
NOT_APPLICABLE              = Config.NOT_APPLICABLE

MENU_CATEGORY               = Config.MENU_CATEGORY
MENU_LUNCH                  = Config.MENU_LUNCH
MENU_DINNER                 = Config.MENU_DINNER

ORDER_STATUS                = Config.ORDER_STATUS
ORDER_STATUS_DICT           = Config.ORDER_STATUS_DICT

KAKAO_PARAM_USER_ID         = Config.KAKAO_PARAM_USER_ID
KAKAO_PARAM_ORDER_ID        = Config.KAKAO_PARAM_ORDER_ID
KAKAO_PARAM_STORE_ID        = Config.KAKAO_PARAM_STORE_ID
KAKAO_PARAM_MENU_ID         = Config.KAKAO_PARAM_MENU_ID

KAKAO_PARAM_STATUS          = Config.KAKAO_PARAM_STATUS
KAKAO_PARAM_STATUS_OK       = Config.KAKAO_PARAM_STATUS_OK
KAKAO_PARAM_STATUS_NOT_OK   = Config.KAKAO_PARAM_STATUS_NOT_OK

ORDER_SUPER_USER_ID         = Config.DEFAULT_USER_ID

#STATIC CONFIG
ORDER_LIST_LENGTH           = 10

def sellingTimeCheck():
    nowDate               = pytz.timezone(TIME_ZONE).localize(datetime.now())
    nowDateWithoutTime    = nowDate.replace(hour=0, minute=0, second=0, microsecond=0)

    # Lunch Order Time 16:30 ~ 10:30
    lunchOrderTimeStart   = nowDateWithoutTime + timedelta(hours=16, minutes=30) 
    lunchOrderTimeEnd     = nowDateWithoutTime + timedelta(hours=10, minutes=30, days=1)

    # Dinner Order Time 10:30 ~ 16:30
    dinnerOrderTimeStart  = nowDateWithoutTime + timedelta(hours=10, minutes=30)
    dinnerOrderTimeEnd    = nowDateWithoutTime + timedelta(hours=16, minutes=30)
    
    if(lunchOrderTimeStart < nowDate) and (nowDate <  lunchOrderTimeEnd):
        return MENU_LUNCH
    elif(dinnerOrderTimeStart < nowDate) and (nowDate <  dinnerOrderTimeEnd):
        return MENU_DINNER
    else:
        errorView("Invalid Selling Time")
        return None


def editOrderTimeCheck(orderInstance):
    menuInstance              = orderInstance.menuInstance

    orderDate                 = orderInstance.order_date
    orderDateWithoutTime      = orderDate.replace(hour=0, minute=0, second=0, microsecond=0)

    nowDate                   = pytz.timezone(TIME_ZONE).localize(datetime.now())
    nowDateWithoutTime        = nowDate.replace(hour=0, minute=0, second=0, microsecond=0)

    # Lunch Order Edit Time 16:30 ~ 9:30(~ 10:30)
    lunchOrderEditTimeStart   = nowDateWithoutTime + timedelta(hours=16, minutes=30, days=-1)
    lunchOrderEditTimeEnd     = nowDateWithoutTime + timedelta(hours=9, minutes=30)
    lunchOrderTimeEnd         = nowDateWithoutTime + timedelta(hours=10, minutes=30)

    # Dinner Order Edit Time 10:30 ~ 15:30(~ 16:30)
    dinnerOrderEditTimeStart  = nowDateWithoutTime + timedelta(hours=10, minutes=30)
    dinnerOrderEditTimeEnd    = nowDateWithoutTime + timedelta(hours=15, minutes=30)
    dinnerOrderTimeEnd        = nowDateWithoutTime + timedelta(hours=16, minutes=30)

    # Lunch Order
    if MENU_CATEGORY[MENU_LUNCH][0] == menuInstance.sellingTime:
        # Today Order
        if(lunchOrderEditTimeStart <= nowDate) and ( nowDate <= lunchOrderEditTimeEnd):
            if nowDate <= lunchOrderEditTimeEnd:
                orderInstance.status = ORDER_STATUS[ORDER_STATUS_DICT['주문 완료']][0]
                orderInstance.save()

            else:
                orderInstance.status = ORDER_STATUS[ORDER_STATUS_DICT['픽업 준비중']][0]
                orderInstance.save()
                
        # Tomorrow Lunch order
        elif lunchOrderTimeEnd <= nowDate:
            orderInstance.status = ORDER_STATUS[ORDER_STATUS_DICT['주문 완료']][0]
            orderInstance.save()

        # Invalid Time Range
        else:
            orderInstance.status = ORDER_STATUS[ORDER_STATUS_DICT['주문 만료']][0]
            orderInstance.save()    

    # Dinner Order
    elif MENU_CATEGORY[MENU_DINNER][0] == menuInstance.sellingTime:
        # Today Order
        if(dinnerOrderEditTimeStart <= nowDate) and ( nowDate <= dinnerOrderTimeEnd):
            if orderDate <= dinnerOrderEditTimeEnd:
                orderInstance.status = ORDER_STATUS[ORDER_STATUS_DICT['주문 완료']][0]
                orderInstance.save()

            else:
                orderInstance.status = ORDER_STATUS[ORDER_STATUS_DICT['픽업 준비중']][0]
                orderInstance.save()
        # Invalid Time Range
        else:
            orderInstance.status = ORDER_STATUS[ORDER_STATUS_DICT['주문 만료']][0]
            orderInstance.save()    
        
    # Invalid Order
    else:
        orderInstance.status = ORDER_STATUS[ORDER_STATUS_DICT['주문 만료']][0]
        orderInstance.save()    
        
    return orderInstance.status

def CouponListup(userID):
    ORDER_LIST_QUICKREPLIES_MAP = [{'action': "message", 'label': "홈으로 돌아가기",    'messageText': "홈으로 돌아가기", 'blockid': "none", 'extra': { KAKAO_PARAM_STATUS: KAKAO_PARAM_STATUS_OK }},
                                   {'action': "message", 'label': "새로고침",    'messageText': "식권 보기", 'blockid': "none", 'extra': { KAKAO_PARAM_STATUS: KAKAO_PARAM_STATUS_OK }}]
                                   
    OrderList = Order.objects.filter(userInstance__id=userID).exclude(
        status=ORDER_STATUS[ORDER_STATUS_DICT['픽업 완료']][0]
    ).exclude(
        status=ORDER_STATUS[ORDER_STATUS_DICT['주문 만료']][0]
    ).exclude(
        status=ORDER_STATUS[ORDER_STATUS_DICT['주문 취소']][0]
    )[:ORDER_LIST_LENGTH]

    # Order Update
    for order in OrderList:
        editOrderTimeCheck(order)

    OrderList = Order.objects.filter(userInstance__id=userID).exclude(
        status=ORDER_STATUS[ORDER_STATUS_DICT['픽업 완료']][0]
    ).exclude(
        status=ORDER_STATUS[ORDER_STATUS_DICT['주문 만료']][0]
    ).exclude(
        status=ORDER_STATUS[ORDER_STATUS_DICT['주문 취소']][0]
    )[:ORDER_LIST_LENGTH]

    # Listup Conpons
    if OrderList:
        KakaoForm = Kakao_CarouselForm()
        KakaoForm.BasicCard_Init()

        for order in OrderList:
            thumbnail = { "imageUrl": "" }

            kakaoMapUrl = "https://map.kakao.com/link/map/{},{}".format(order.storeInstance.name, getLatLng(order.storeInstance.addr))

            buttons = [
                {'action': "webLink", 'label': "위치보기",  "webLinkUrl": kakaoMapUrl},
            ]

            # CAN EDIT COUPONS
            if ORDER_STATUS_DICT[order.status] <= ORDER_STATUS_DICT['주문 완료']: 
                buttons.append({'action': "message", 'label': "주문 취소 하기",  'messageText': "주문 취소 하기", 
                'extra': { KAKAO_PARAM_ORDER_ID: order.id }})
                buttons.append({'action': "message", 'label': "픽업 시간 변경",  'messageText': "{} 픽업시간 변경".format(order.menuInstance.sellingTime), 
                'extra': { KAKAO_PARAM_ORDER_ID: order.id }})
                
            # CAN'T EDIT COUPONS
            elif ORDER_STATUS_DICT[order.status] == ORDER_STATUS_DICT['픽업 가능']: 
                buttons.append({'action': "message", 'label': "식권 사용하기",  'messageText': "식권 사용 확인", 
                'extra': { KAKAO_PARAM_ORDER_ID: order.id }})

            else:
                errorView("Invalid Case on order status check by now time.")

            #if CAN CHANGE PICKUP TIME:
            #    buttons.append({'action': "message", 'label': "픽업 시간 변경",  'messageText': "픽업 시간 변경", 'extra': { }})

            KakaoForm.BasicCard_Add(
                "주문번호: {}".format(order.management_code),
                " - 주문자: {}\n\n - 매장: {} \n - 메뉴: {}\n\n - 결제 금액: {}원\n - 픽업 시간: {}\n\n - 주문 상태: {}".format(
                    order.userInstance.name,
                    order.storeInstance.name, 
                    order.menuInstance.name, 
                    order.menuInstance.price, 
                    order.pickupTime.strftime('%H시%M분 %m월%d일'),
                    order.status
                ),
                thumbnail, buttons
            )

    # No Coupons
    else:
        KakaoForm = Kakao_SimpleForm()
        KakaoForm.SimpleForm_Init()

        ORDER_LIST_QUICKREPLIES_MAP.append({'action': "message", 'label': "주문 하기",    'messageText': "주문 시간 선택", 'blockid': "none", 'extra': { KAKAO_PARAM_STATUS: KAKAO_PARAM_STATUS_OK }})
        
        KakaoForm.SimpleText_Add("현재 조회 가능한 식권이 없습니다!\n주문하시려면 아래 [주문 하기]를 눌러주세요!")

    for entryPoint in ORDER_LIST_QUICKREPLIES_MAP:
        KakaoForm.QuickReplies_Add(entryPoint['action'], entryPoint['label'], entryPoint['messageText'], entryPoint['blockid'], entryPoint['extra'])

    return JsonResponse(KakaoForm.GetForm())
'''
    @name OrderListup
    @param userID, order_status

    @note
    @bug
    @todo userName to real username, now just use super user("잇플").
'''
def OrderListup(userID):
    ORDER_LIST_QUICKREPLIES_MAP = [{'action': "message", 'label': "홈으로 돌아가기",    'messageText': "홈으로 돌아가기", 'blockid': "none", 'extra': { KAKAO_PARAM_STATUS: KAKAO_PARAM_STATUS_OK }},
                                   {'action': "message", 'label': "새로고침",    'messageText': "주문 내역", 'blockid': "none", 'extra': { KAKAO_PARAM_STATUS: KAKAO_PARAM_STATUS_OK }}]

    OrderList = Order.objects.filter(userInstance__id=userID).exclude(
        status=ORDER_STATUS[ORDER_STATUS_DICT['주문 확인중']][0]
    ).exclude(
        status=ORDER_STATUS[ORDER_STATUS_DICT['주문 완료']][0]
    ).exclude(
        status=ORDER_STATUS[ORDER_STATUS_DICT['픽업 준비중']][0]
    ).exclude(
        status=ORDER_STATUS[ORDER_STATUS_DICT['픽업 가능']][0]
    )[:ORDER_LIST_LENGTH]
    
    if OrderList:
        KakaoForm = Kakao_CarouselForm()
        KakaoForm.BasicCard_Init()

        for order in OrderList:
            thumbnail = { "imageUrl": "" }

            kakaoMapUrl = "https://map.kakao.com/link/map/{},{}".format(order.storeInstance.name, getLatLng(order.storeInstance.addr))

            buttons = [
                {'action': "webLink", 'label': "위치보기",  "webLinkUrl": kakaoMapUrl},
            ]


            # CAN"T USE COUPONS
            if ORDER_STATUS_DICT[order.status] > ORDER_STATUS_DICT['픽업 가능']:
                KakaoForm.BasicCard_Add(
                    "주문번호: {}".format(order.management_code),
                    " - 주문자: {}\n\n - 매장: {} \n - 메뉴: {}\n\n - 결제 금액: {}원\n - 픽업 시간: {}\n\n - 주문 상태: {}".format(
                        order.userInstance.name,
                        order.storeInstance.name, 
                        order.menuInstance.name, 
                        order.menuInstance.price, 
                        order.pickupTime.strftime('%H시%M분 %m월%d일'),
                        order.status
                    ),
                    thumbnail, buttons
                )
    else:
        KakaoForm = Kakao_SimpleForm()
        KakaoForm.SimpleForm_Init()

        ORDER_LIST_QUICKREPLIES_MAP.append({'action': "message", 'label': "주문 하기",    'messageText': "주문 시간 선택", 'blockid': "none", 'extra': { KAKAO_PARAM_STATUS: KAKAO_PARAM_STATUS_OK }})

        KakaoForm.SimpleText_Add("주문 내역이 존재하지 않습니다!\n주문하시려면 아래 [주문 하기]를 눌러주세요!")
 
    for entryPoint in ORDER_LIST_QUICKREPLIES_MAP:
        KakaoForm.QuickReplies_Add(entryPoint['action'], entryPoint['label'], entryPoint['messageText'], entryPoint['blockid'], entryPoint['extra'])

    return JsonResponse(KakaoForm.GetForm())

'''
    @name getOrderList
    @param userID

    @note
    @bug
    @tood
'''
@csrf_exempt
def getOrderList(request):
    try:
        kakaoPayload = KakaoPayLoad(request)

        # Invalied Path Access
        #if(kakaoPayload.userID == NOT_APPLICABLE):
        #    return errorView("Parameter Invalid")
        #else:
        #    UserInstance = User.objects.get(id=kakaoPayload.userID)

        EatplusSkillLog("Order Check Flow")

        return OrderListup(ORDER_SUPER_USER_ID)

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView("{} ".format(ex))


'''
    @name getCoupon
    @param userID

    @note
    @bug
    @tood
'''
@csrf_exempt
def getCoupon(request):
    try:
        kakaoPayload = KakaoPayLoad(request)

        # Invalied Path Access
        #if(kakaoPayload.userID == NOT_APPLICABLE):
        #    return errorView("Parameter Invalid")
        #else:
        #    UserInstance = User.objects.get(id=kakaoPayload.userID)


        EatplusSkillLog("Order Check Flow")

        return CouponListup(ORDER_SUPER_USER_ID)

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView("{} ".format(ex))

'''
    @name useCoupon
    @param orderID

    @note
    @bug
    @tood
'''
@csrf_exempt
def confirmUseCoupon(request):
    try:
        kakaoPayload = KakaoPayLoad(request)

        # Invalied Path Access
        #if(kakaoPayload.userID == NOT_APPLICABLE):
        #    return errorView("Parameter Invalid")
        #else:
        #    UserInstance = User.objects.get(id=kakaoPayload.userID)
        if(kakaoPayload.orderID == NOT_APPLICABLE):
            return errorView("Parameter Invalid")
        else:
            OrderInstance = Order.objects.get(id=kakaoPayload.orderID)

        USE_COUPON_QUICKREPLIES_MAP = [                
            {'action': "message", 'label': "사용하기",    'messageText': "식권 사용", 'blockid': "none", 'extra': { KAKAO_PARAM_ORDER_ID: OrderInstance.id }},
            {'action': "message", 'label': "취소하기",    'messageText': "식권 사용 취소", 'blockid': "none", 'extra': { KAKAO_PARAM_STATUS: KAKAO_PARAM_STATUS_OK }},
        ]

        EatplusSkillLog("Order Check Flow")

        KakaoForm = Kakao_SimpleForm()
        KakaoForm.SimpleForm_Init()

        thumbnail = { "imageUrl": "" }

        buttons = [
            # No Buttons
        ]

        KakaoForm.SimpleText_Add("식권을 사용하시겠습니까?")

        for entryPoint in USE_COUPON_QUICKREPLIES_MAP:
            KakaoForm.QuickReplies_Add(entryPoint['action'], entryPoint['label'], entryPoint['messageText'], entryPoint['blockid'], entryPoint['extra'])
        
        return JsonResponse(KakaoForm.GetForm())

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView("{} ".format(ex))
