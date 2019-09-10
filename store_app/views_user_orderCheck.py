#Django Library
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils import timezone

from django.conf import settings

#External Library
from datetime import datetime, timedelta
import pytz

import requests
import json
import sys



#Models 
from .models_config import Config, dateNowByTimeZone

from .models_user  import User
from .models_order import Order, OrderManager
from .models_store import Store, Menu, Category, SubCategory

#View Modules
from .module_KakaoForm import Kakao_SimpleForm, Kakao_CarouselForm

#View
from .views_kakaoTool import getLatLng, KakaoPayLoad
from .views_system import EatplusSkillLog, errorView

#GLOBAL CONFIG
TIME_ZONE                   = Config.TIME_ZONE
NOT_APPLICABLE              = Config.NOT_APPLICABLE

SELLING_TIME_LUNCH          = Config.SELLING_TIME_LUNCH
SELLING_TIME_DINNER         = Config.SELLING_TIME_DINNER
SELLING_TIME_CATEGORY_DICT  = Config.SELLING_TIME_CATEGORY_DICT
SELLING_TIME_CATEGORY       = Config.SELLING_TIME_CATEGORY

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

def CouponListup(userID):
    ORDER_LIST_QUICKREPLIES_MAP = [{'action': "message", 'label': "홈으로 돌아가기",    'messageText': "홈으로 돌아가기", 'blockid': "none", 'extra': { KAKAO_PARAM_STATUS: KAKAO_PARAM_STATUS_OK }},
                                   {'action': "message", 'label': "새로고침",         'messageText': "주문 상태 확인", 'blockid': "none", 'extra': { KAKAO_PARAM_STATUS: KAKAO_PARAM_STATUS_OK }}]

    OrderManagerInstance = OrderManager(userID)

    availableCoupons = OrderManagerInstance.availableCouponStatusUpdate()

    # Listup Conpons
    if availableCoupons:
        KakaoForm = Kakao_CarouselForm()
        KakaoForm.BasicCard_Init()

        for orderInstance in availableCoupons:
            thumbnail = { "imageUrl": "" }

            kakaoMapUrl = "https://map.kakao.com/link/map/{},{}".format(orderInstance.storeInstance.name, getLatLng(orderInstance.storeInstance.addr))

            buttons = [
                {'action': "webLink", 'label': "위치보기",  "webLinkUrl": kakaoMapUrl},
            ]

            # CAN EDIT COUPONS
            if ORDER_STATUS_DICT[orderInstance.status] <= ORDER_STATUS_DICT['주문 완료']: 
                buttons.append({'action': "message", 'label': "주문 취소 하기",  'messageText': "주문 취소 하기", 
                'extra': { KAKAO_PARAM_ORDER_ID: orderInstance.id }})
                buttons.append({'action': "message", 'label': "픽업 시간 변경",  'messageText': "{} 픽업시간 변경".format(orderInstance.menuInstance.sellingTime), 
                'extra': { KAKAO_PARAM_ORDER_ID: orderInstance.id }})
                
            # CAN'T EDIT COUPONS
            elif ORDER_STATUS_DICT[orderInstance.status] == ORDER_STATUS_DICT['픽업 가능']: 
                buttons.append({'action': "message", 'label': "식권 사용하기",  'messageText': "식권 사용 확인", 
                'extra': { KAKAO_PARAM_ORDER_ID: orderInstance.id }})

            else:
                errorView("Invalid Case on order status check by now time.")

            #if CAN CHANGE PICKUP TIME:
            #    buttons.append({'action': "message", 'label': "픽업 시간 변경",  'messageText': "픽업 시간 변경", 'extra': { }})
            KakaoForm.BasicCard_Add(
                "주문번호: {}".format(orderInstance.management_code),
                " - 주문자: {}\n\n - 매장: {} \n - 메뉴: {}\n\n - 결제 금액: {}원\n - 픽업 시간: {}\n\n - 주문 상태: {}".format(
                    orderInstance.userInstance.name,
                    orderInstance.storeInstance.name, 
                    orderInstance.menuInstance.name, 
                    orderInstance.menuInstance.price, 
                    orderInstance.pickupTime.strftime('%H시%M분 %m월%d일'),
                    orderInstance.status
                ),
                thumbnail, buttons
            )

    # No Coupons
    else:
        KakaoForm = Kakao_SimpleForm()
        KakaoForm.SimpleForm_Init()

        ORDER_LIST_QUICKREPLIES_MAP.append({'action': "message", 'label': "주문 하기",    'messageText': "주문시간 선택", 'blockid': "none", 'extra': { KAKAO_PARAM_STATUS: KAKAO_PARAM_STATUS_OK, KAKAO_PARAM_USER_ID: ORDER_SUPER_USER_ID }})
        
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
                                   {'action': "message", 'label': "새로고침",    'messageText': "최근 구매내역", 'blockid': "none", 'extra': { KAKAO_PARAM_STATUS: KAKAO_PARAM_STATUS_OK }}]

    OrderManagerInstance = OrderManager(userID)
    
    unavailableCoupons = OrderManagerInstance.getUnavailableCoupons()[:ORDER_LIST_LENGTH]

    if unavailableCoupons:
        KakaoForm = Kakao_CarouselForm()
        KakaoForm.BasicCard_Init()

        for orderInstance in unavailableCoupons:
            thumbnail = { "imageUrl": "" }

            kakaoMapUrl = "https://map.kakao.com/link/map/{},{}".format(orderInstance.storeInstance.name, getLatLng(orderInstance.storeInstance.addr))

            buttons = [
                {'action': "webLink", 'label': "위치보기",  "webLinkUrl": kakaoMapUrl},
            ]


            # CAN"T USE COUPONS
            if ORDER_STATUS_DICT[orderInstance.status] > ORDER_STATUS_DICT['픽업 가능']:
                KakaoForm.BasicCard_Add(
                    "주문번호: {}".format(orderInstance.management_code),
                    " - 주문자: {}\n\n - 매장: {} \n - 메뉴: {}\n\n - 결제 금액: {}원\n - 픽업 시간: {}\n\n - 주문 상태: {}".format(
                        orderInstance.userInstance.name,
                        orderInstance.storeInstance.name, 
                        orderInstance.menuInstance.name, 
                        orderInstance.menuInstance.price, 
                        orderInstance.pickupTime.strftime('%H시%M분 %m월%d일'),
                        orderInstance.status
                    ),
                    thumbnail, buttons
                )
    else:
        KakaoForm = Kakao_SimpleForm()
        KakaoForm.SimpleForm_Init()

        ORDER_LIST_QUICKREPLIES_MAP.append({'action': "message", 'label': "주문 하기",    'messageText': "주문시간 선택", 'blockid': "none", 'extra': { KAKAO_PARAM_STATUS: KAKAO_PARAM_STATUS_OK, KAKAO_PARAM_USER_ID: ORDER_SUPER_USER_ID }})

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