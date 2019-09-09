#Django Library
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

#External Library
import requests
import json

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
NOT_APPLICABLE              = Config.NOT_APPLICABLE

MENU_LUNCH                  = Config.MENU_LUNCH
MENU_DINNER                 = Config.MENU_DINNER
MENU_CATEGORY_DICT          = Config.MENU_CATEGORY_DICT
MENU_CATEGORY               = Config.MENU_CATEGORY

ORDER_STATUS                = Config.ORDER_STATUS
ORDER_STATUS_DICT           = Config.ORDER_STATUS_DICT

KAKAO_PARAM_USER_ID         = Config.KAKAO_PARAM_USER_ID
KAKAO_PARAM_ORDER_ID        = Config.KAKAO_PARAM_ORDER_ID
KAKAO_PARAM_STORE_ID        = Config.KAKAO_PARAM_STORE_ID
KAKAO_PARAM_MENU_ID         = Config.KAKAO_PARAM_MENU_ID

KAKAO_PARAM_PICKUP_TIME     = Config.KAKAO_PARAM_PICKUP_TIME

KAKAO_PARAM_STATUS          = Config.KAKAO_PARAM_STATUS
KAKAO_PARAM_STATUS_OK       = Config.KAKAO_PARAM_STATUS_OK
KAKAO_PARAM_STATUS_NOT_OK   = Config.KAKAO_PARAM_STATUS_NOT_OK

#STATIC CONFIG

DEFAULT_QUICKREPLIES_MAP = [                
    {'action': "message", 'label': "홈으로 돌아가기",    'messageText': "홈으로 돌아가기", 'blockid': "none", 
        'extra': { KAKAO_PARAM_STATUS: KAKAO_PARAM_STATUS_OK }},
]


# # # # # # # # # # # # # # # # # # # # # # # # #
#
# Static View
#
# # # # # # # # # # # # # # # # # # # # # # # # #

# # # # # # # # # # # # # # # # # # # # # # # # #
#
# External View
#
# # # # # # # # # # # # # # # # # # # # # # # # #
DEFAULT_QUICKREPLIES_MAP = [                
    {'action': "message", 'label': "홈으로 돌아가기",    'messageText': "홈으로 돌아가기", 'blockid': "none", 
        'extra': { KAKAO_PARAM_STATUS: KAKAO_PARAM_STATUS_OK }},
]

'''
    @name orderCancle
    @param name

    @note
    @bug
    @tood
'''
@csrf_exempt
def orderCancel(request):
    try:
        kakaoPayload = KakaoPayLoad(request)

       # Invalied Path Access
        if(kakaoPayload.orderID == NOT_APPLICABLE):
            return errorView("Order Cancel -> Parameter Error")
        else:
            OrderInstance = Order.objects.get(id=kakaoPayload.orderID)

        EatplusSkillLog("Order Cancel Flow", "Order Cancel")

        OrderInstance.status = Config.ORDER_STATUS[Config.ORDER_STATUS_DICT['주문 취소']][0]
        OrderInstance.save()
        
        KakaoForm = Kakao_CarouselForm()
        KakaoForm.BasicCard_Init()

        thumbnail = { "imageUrl": "" }

        kakaoMapUrl = "https://map.kakao.com/link/map/{},{}".format(OrderInstance.storeInstance.name, getLatLng(OrderInstance.storeInstance.addr))

        buttons = [
            {'action': "webLink", 'label': "위치보기",  "webLinkUrl": kakaoMapUrl},
        ]

        KakaoForm.BasicCard_Add(
            "식권이 취소되었습니다.",
            "주문번호: {}\n--------------------\n - 주문자: {}\n\n - 매장: {} \n - 메뉴: {}\n\n - 결제 금액: {}원\n\n - 픽업 시간: {}\n--------------------\n - 매장 위치: {}".format(
                OrderInstance.management_code,
                OrderInstance.userInstance.name,
                OrderInstance.storeInstance.name, 
                OrderInstance.menuInstance.name, 
                OrderInstance.menuInstance.price, 
                OrderInstance.pickupTime, 
                OrderInstance.storeInstance.addr
            ),
            thumbnail, buttons
        )

        for entryPoint in DEFAULT_QUICKREPLIES_MAP:
            KakaoForm.QuickReplies_Add(entryPoint['action'], entryPoint['label'], entryPoint['messageText'], entryPoint['blockid'], entryPoint['extra'])
        
        return JsonResponse(KakaoForm.GetForm())

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView("Order Cancel Error\n- {} ".format(ex))


@csrf_exempt
def getOrderPickupTime(request):
    try:
        kakaoPayload = KakaoPayLoad(request)

        # Invalied Path Access
        if(kakaoPayload.orderID == NOT_APPLICABLE) or (kakaoPayload.sellingTime == NOT_APPLICABLE):
            return errorView("Get Pickup Time -> Parameter Error\n {} \n {}".format(kakaoPayload.storeID, kakaoPayload.menuID))
        else:
            orderInstance = Order.objects.get(id=kakaoPayload.orderID)

        EatplusSkillLog("Order Flow", "Get Order Picktime")

        KakaoForm = Kakao_SimpleForm()
        KakaoForm.SimpleForm_Init()

        KakaoForm.SimpleText_Add("변경 하실 픽업 시간을 설정해주세요.")

        PICKUP_TIME_QUICKREPLIES_MAP = []

        LUNCH_PICKUP_TIME_MAP  = [ "11:30", "11:45", "12:00", "12:15", "12:30", "12:45", "13:00", "13:15", "13:30" ]
        DINNER_PICKUP_TIME_MAP = [ "17:30", "18:00", "18:30", "19:00", "19:30", "20:00", "20:30", "21:00" ]
        if MENU_CATEGORY_DICT[kakaoPayload.sellingTime] == MENU_LUNCH:
            ENTRY_PICKUP_TIME_MAP = LUNCH_PICKUP_TIME_MAP
        else:
            ENTRY_PICKUP_TIME_MAP = DINNER_PICKUP_TIME_MAP

        allExtraData = kakaoPayload.dataActionExtra

        for pickupTime in ENTRY_PICKUP_TIME_MAP:
            PICKUP_TIME_QUICKREPLIES_MAP += {'action': "message", 'label': pickupTime, 'messageText': "픽업 시간 변경 완료", 'blockid': "none", 'extra': { **allExtraData, KAKAO_PARAM_PICKUP_TIME: pickupTime}},

        for entryPoint in PICKUP_TIME_QUICKREPLIES_MAP:
            KakaoForm.QuickReplies_Add(entryPoint['action'], entryPoint['label'], entryPoint['messageText'], entryPoint['blockid'], entryPoint['extra'])

        return JsonResponse(KakaoForm.GetForm())

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView("Get Pickup Time Error\n- {} ".format(ex))


'''
    @name orderPickupTimeChange
    @param name

    @note
    @bug
    @tood
'''
@csrf_exempt
def orderPickupTimeChange(request):
    try:
        kakaoPayload = KakaoPayLoad(request)

       # Invalied Path Access
        if (kakaoPayload.orderID == NOT_APPLICABLE) or kakaoPayload.pickupTime == NOT_APPLICABLE:
            return errorView("Order Pickup Time Change -> Parameter Error")
        else:
            OrderInstance = Order.objects.get(id=kakaoPayload.orderID)

        EatplusSkillLog("Order Pickup Time Change Flow", "Order Pickup Time Change")

        beforePickupTime = OrderInstance.pickupTime
        OrderInstance.pickupTime = kakaoPayload.pickupTime
        OrderInstance.save()
        
        KakaoForm = Kakao_CarouselForm()
        KakaoForm.BasicCard_Init()

        thumbnail = { "imageUrl": "" }

        kakaoMapUrl = "https://map.kakao.com/link/map/{},{}".format(OrderInstance.storeInstance.name, getLatLng(OrderInstance.storeInstance.addr))

        buttons = [
            {'action': "webLink", 'label': "위치보기",  "webLinkUrl": kakaoMapUrl},
        ]

        KakaoForm.BasicCard_Add(
            "픽업 시간이 {} 에서 {} 으로 변경되었습니다.".format(beforePickupTime, OrderInstance.pickupTime),
            "주문번호: {}\n--------------------\n - 주문자: {}\n\n - 매장: {} \n - 메뉴: {}\n\n - 결제 금액: {}원\n\n - 픽업 시간: {}\n--------------------\n - 매장 위치: {}".format(
                OrderInstance.management_code,
                OrderInstance.userInstance.name,
                OrderInstance.storeInstance.name, 
                OrderInstance.menuInstance.name, 
                OrderInstance.menuInstance.price, 
                OrderInstance.pickupTime, 
                OrderInstance.storeInstance.addr
            ),
            thumbnail, buttons
        )

        for entryPoint in DEFAULT_QUICKREPLIES_MAP:
            KakaoForm.QuickReplies_Add(entryPoint['action'], entryPoint['label'], entryPoint['messageText'], entryPoint['blockid'], entryPoint['extra'])
        
        return JsonResponse(KakaoForm.GetForm())

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView("Order Cancel Error\n- {} ".format(ex))




