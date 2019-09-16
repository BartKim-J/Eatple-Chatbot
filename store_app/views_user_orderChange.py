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
from .views_wording import wordings

#GLOBAL CONFIG
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

KAKAO_PARAM_PICKUP_TIME     = Config.KAKAO_PARAM_PICKUP_TIME

KAKAO_PARAM_STATUS          = Config.KAKAO_PARAM_STATUS
KAKAO_PARAM_STATUS_OK       = Config.KAKAO_PARAM_STATUS_OK
KAKAO_PARAM_STATUS_NOT_OK   = Config.KAKAO_PARAM_STATUS_NOT_OK

ORDER_SUPER_USER_ID         = Config.DEFAULT_USER_ID

# # # # # # # # # # # # # # # # # # # # # # # # #
#
# Static View
#
# # # # # # # # # # # # # # # # # # # # # # # # #
DEFAULT_QUICKREPLIES_MAP = [                
    {'action': "message", 'label': wordings.RETURN_HOME_QUICK_REPLISE,    'messageText': wordings.RETURN_HOME_QUICK_REPLISE, 'blockid': "none", 
        'extra': { KAKAO_PARAM_STATUS: KAKAO_PARAM_STATUS_OK }},
]

# # # # # # # # # # # # # # # # # # # # # # # # #
#
# External View
#
# # # # # # # # # # # # # # # # # # # # # # # # #
'''
    @name orderCancle
    @param orderID

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
            return errorView("Parameter Invalid")
        else:
            orderInstance = Order.objects.get(id=kakaoPayload.orderID)

        EatplusSkillLog("Order Change Flow")

        orderInstance.status = ORDER_STATUS[ORDER_STATUS_DICT['주문 취소']][0]
        orderInstance.save()
        
        KakaoForm = Kakao_CarouselForm()
        KakaoForm.BasicCard_Init()

        thumbnail = { "imageUrl": "" }

        kakaoMapUrl = "https://map.kakao.com/link/map/{},{}".format(orderInstance.storeInstance.name, getLatLng(orderInstance.storeInstance.addr))

        buttons = [
            {'action': "webLink", 'label': wordings.SHOW_LOCATION_BTN,  "webLinkUrl": kakaoMapUrl},
        ]

        KakaoForm.BasicCard_Add(
            "주문이 취소되었습니다. ",
            "주문번호: {}\n--------------------\n - 주문자: {}\n\n - 매장: {} \n - 메뉴: {}\n\n - 결제 금액: {}원\n\n - 픽업 시간: {}\n--------------------\n - 매장 위치: {}".format(
                orderInstance.management_code,
                orderInstance.userInstance.name,
                orderInstance.storeInstance.name, 
                orderInstance.menuInstance.name, 
                orderInstance.menuInstance.price, 
                orderInstance.pickupTime.astimezone().strftime('%H시%M분 %m월%d일'), 
                orderInstance.storeInstance.addr
            ),
            thumbnail, buttons
        )

        for entryPoint in DEFAULT_QUICKREPLIES_MAP:
            KakaoForm.QuickReplies_Add(entryPoint['action'], entryPoint['label'], entryPoint['messageText'], entryPoint['blockid'], entryPoint['extra'])
        
        return JsonResponse(KakaoForm.GetForm())

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView("{} ".format(ex))

'''
    @name getOrderPickupTime
    @param orderID, sellingTime

    @note
    @bug
    @tood
'''
@csrf_exempt
def getOrderPickupTime(request):
    try:
        kakaoPayload = KakaoPayLoad(request)

        # Invalied Path Access
        if(kakaoPayload.orderID == NOT_APPLICABLE) or (kakaoPayload.sellingTime == NOT_APPLICABLE):
            return errorView("Parameter Invalid")
        else:
            orderInstance = Order.objects.get(id=kakaoPayload.orderID)

        EatplusSkillLog("Order Change Flow")

        KakaoForm = Kakao_SimpleForm()
        KakaoForm.SimpleForm_Init()

        KakaoForm.SimpleText_Add("변경 하실 픽업 시간을 설정해주세요.")

        PICKUP_TIME_QUICKREPLIES_MAP = []

        LUNCH_PICKUP_TIME_MAP  = [ "11:30", "11:45", "12:00", "12:15", "12:30", "12:45", "13:00", "13:15", "13:30" ]
        DINNER_PICKUP_TIME_MAP = [ "17:30", "18:00", "18:30", "19:00", "19:30", "20:00", "20:30", "21:00" ]
        if SELLING_TIME_CATEGORY_DICT[kakaoPayload.sellingTime] == SELLING_TIME_LUNCH:
            ENTRY_PICKUP_TIME_MAP = LUNCH_PICKUP_TIME_MAP
        else:
            ENTRY_PICKUP_TIME_MAP = DINNER_PICKUP_TIME_MAP

        allExtraData = kakaoPayload.dataActionExtra

        for pickupTime in ENTRY_PICKUP_TIME_MAP:
            PICKUP_TIME_QUICKREPLIES_MAP += {'action': "message", 'label': pickupTime, 'messageText': wordings.ORDER_PICKUP_TIME_CHANGE_CONFIRM_COMMAND, 'blockid': "none", 'extra': { **allExtraData, KAKAO_PARAM_PICKUP_TIME: pickupTime}},

        for entryPoint in PICKUP_TIME_QUICKREPLIES_MAP:
            KakaoForm.QuickReplies_Add(entryPoint['action'], entryPoint['label'], entryPoint['messageText'], entryPoint['blockid'], entryPoint['extra'])

        return JsonResponse(KakaoForm.GetForm())

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView("{}".format(ex))


'''
    @name orderPickupTimeChange
    @param orderID, pickupTime

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
            return errorView("Parameter Invalid")
        else:
            orderInstance = Order.objects.get(id=kakaoPayload.orderID)

        EatplusSkillLog("Order Change Flow")

        beforePickupTime         = orderInstance.pickupTime
        orderInstance.pickupTime = orderInstance.rowPickupTimeToDatetime(kakaoPayload.pickupTime)
        orderInstance.save()
        
        KakaoForm = Kakao_CarouselForm()
        KakaoForm.BasicCard_Init()

        thumbnail = { "imageUrl": "" }

        kakaoMapUrl = "https://map.kakao.com/link/map/{},{}".format(orderInstance.storeInstance.name, getLatLng(orderInstance.storeInstance.addr))

        buttons = [
            {'action': "webLink", 'label': wordings.SHOW_LOCATION_BTN,  "webLinkUrl": kakaoMapUrl},
        ]

        KakaoForm.BasicCard_Add(
            "픽업시간이 {} 에서 {} 으로 변경되었습니다.".format(beforePickupTime.astimezone().strftime('%H:%M'), orderInstance.pickupTime.astimezone().strftime('%H:%M')),
            "주문번호: {}\n--------------------\n - 주문자: {}\n\n - 매장: {} \n - 메뉴: {}\n\n - 결제 금액: {}원\n\n - 픽업 시간: {}\n--------------------\n - 매장 위치: {}".format(
                orderInstance.management_code,
                orderInstance.userInstance.name,
                orderInstance.storeInstance.name, 
                orderInstance.menuInstance.name, 
                orderInstance.menuInstance.price, 
                orderInstance.pickupTime.astimezone().strftime('%H시%M분 %m월%d일'), 
                orderInstance.storeInstance.addr
            ),
            thumbnail, buttons
        )

        for entryPoint in DEFAULT_QUICKREPLIES_MAP:
            KakaoForm.QuickReplies_Add(entryPoint['action'], entryPoint['label'], entryPoint['messageText'], entryPoint['blockid'], entryPoint['extra'])
        
        return JsonResponse(KakaoForm.GetForm())

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView("{}".format(ex))


'''
    @name useCoupon
    @param orderID

    @note
    @bug
    @tood
'''
@csrf_exempt
def useCoupon(request):
    try:
        kakaoPayload = KakaoPayLoad(request)

        # Invalied Path Access
        if (kakaoPayload.orderID == NOT_APPLICABLE):
            return errorView("Parameter Invalid")
        else:
            orderInstance = Order.objects.get(id=kakaoPayload.orderID)

        EatplusSkillLog("Order Change Flow")

        orderInstance.status = ORDER_STATUS[ORDER_STATUS_DICT['픽업 완료']][0]
        orderInstance.save()
        
        KakaoForm = Kakao_CarouselForm()
        KakaoForm.BasicCard_Init()

        thumbnail = { "imageUrl": "" }

        kakaoMapUrl = "https://map.kakao.com/link/map/{},{}".format(orderInstance.storeInstance.name, getLatLng(orderInstance.storeInstance.addr))

        buttons = [
            # No Buttons
        ]

        KakaoForm.BasicCard_Add(
            "식권이 사용되었습니다.",
            "주문번호: {}\n--------------------\n - 주문자: {}\n\n - 매장: {} \n - 메뉴: {}\n\n - 결제 금액: {}원\n\n - 픽업 시간: {}\n--------------------\n - 매장 위치: {}".format(
                orderInstance.management_code,
                orderInstance.userInstance.name,
                orderInstance.storeInstance.name, 
                orderInstance.menuInstance.name, 
                orderInstance.menuInstance.price, 
                orderInstance.pickupTime.astimezone().strftime('%H시%M분 %m월%d일'), 
                orderInstance.storeInstance.addr
            ),
            thumbnail, buttons
        )

        for entryPoint in DEFAULT_QUICKREPLIES_MAP:
            KakaoForm.QuickReplies_Add(entryPoint['action'], entryPoint['label'], entryPoint['messageText'], entryPoint['blockid'], entryPoint['extra'])
        
        return JsonResponse(KakaoForm.GetForm())

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView("{}".format(ex))






