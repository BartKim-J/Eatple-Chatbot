#Django Library
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

#External Library
import requests
import json
import sys

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

ORDER_STATUS                = Config.ORDER_STATUS
ORDER_STATUS_DICT           = Config.ORDER_STATUS_DICT

KAKAO_PARAM_USER_ID         = Config.KAKAO_PARAM_USER_ID
KAKAO_PARAM_ORDER_ID        = Config.KAKAO_PARAM_ORDER_ID
KAKAO_PARAM_STORE_ID        = Config.KAKAO_PARAM_STORE_ID
KAKAO_PARAM_MENU_ID         = Config.KAKAO_PARAM_MENU_ID

KAKAO_PARAM_STATUS          = Config.KAKAO_PARAM_STATUS
KAKAO_PARAM_STATUS_OK       = Config.KAKAO_PARAM_STATUS_OK
KAKAO_PARAM_STATUS_NOT_OK   = Config.KAKAO_PARAM_STATUS_NOT_OK

#STATIC CONFIG
ORDER_SUPER_USER_NAME       = "잇플"
ORDER_LIST_LENGTH           = 10

'''
    @name OrderListup
    @param name

    @note
    @bug
    @todo userName to real username, now just use super user("잇플").
'''
def OrderListup(name, status):
    ORDER_LIST_QUICKREPLIES_MAP = [{'action': "message", 'label': "홈으로 돌아가기",    'messageText': "홈으로 돌아가기", 'blockid': "none", 'extra': { KAKAO_PARAM_STATUS: KAKAO_PARAM_STATUS_OK }},]

    
    if status == NOT_APPLICABLE: # Order List
        ORDER_LIST_QUICKREPLIES_MAP.append({'action': "message", 'label': "새로고침",    'messageText': "주문 내역", 'blockid': "none", 'extra': { KAKAO_PARAM_STATUS: KAKAO_PARAM_STATUS_OK }})        
    
    else: # Coupon List
        ORDER_LIST_QUICKREPLIES_MAP.append({'action': "message", 'label': "새로고침",    'messageText': "식권 보기", 'blockid': "none", 'extra': { KAKAO_PARAM_STATUS: KAKAO_PARAM_STATUS_OK }})

    OrderList = Order.objects.filter(userInstance__name=name)[:ORDER_LIST_LENGTH]
    if OrderList:
        KakaoForm = Kakao_CarouselForm()
        KakaoForm.BasicCard_Init()

        for order in OrderList:
            thumbnail = { "imageUrl": "" }

            kakaoMapUrl = "https://map.kakao.com/link/map/{},{}".format(order.storeInstance.name, getLatLng(order.storeInstance.addr))

            buttons = [
                {'action': "webLink", 'label': "위치보기",  "webLinkUrl": kakaoMapUrl},
            ]

            if status == NOT_APPLICABLE:

                if ORDER_STATUS_DICT[order.status] > ORDER_STATUS_DICT['픽업 준비중']:
                    KakaoForm.BasicCard_Add(
                        "주문번호: {}".format(order.management_code),
                        " - 주문자: {}\n\n - 매장: {} \n - 메뉴: {}\n\n - 결제 금액: {}원\n - 픽업 시간: {}\n\n - 주문 상태: {}".format(
                            order.userInstance.name,
                            order.storeInstance.name, 
                            order.menuInstance.name, 
                            order.menuInstance.price, 
                            order.pickupTime,
                            order.status
                        ),
                        thumbnail, buttons
                    )
            # Coupon List
            else:
                if ORDER_STATUS_DICT[order.status] <= ORDER_STATUS_DICT['픽업 준비중']:

                    if ORDER_STATUS_DICT[order.status] < ORDER_STATUS_DICT['픽업 준비중']:
                        buttons.append({'action': "message", 'label': "주문 취소 하기",  'messageText': "주문 취소 하기", 
                        'extra': { KAKAO_PARAM_ORDER_ID: order.id }})
                        buttons.append({'action': "message", 'label': "픽업 시간 변경",  'messageText': "{} 픽업시간 변경".format(order.menuInstance.sellingTime), 
                        'extra': { KAKAO_PARAM_ORDER_ID: order.id }})
                    else:
                        buttons.append({'action': "message", 'label': "식권 사용하기",  'messageText': "식권 사용 확인", 
                        'extra': { KAKAO_PARAM_ORDER_ID: order.id }})
                    #if CAN CHANGE PICKUP TIME:
                    #    buttons.append({'action': "message", 'label': "픽업 시간 변경",  'messageText': "픽업 시간 변경", 'extra': { }})

                    KakaoForm.BasicCard_Add(
                        "주문번호: {}".format(order.management_code),
                        " - 주문자: {}\n\n - 매장: {} \n - 메뉴: {}\n\n - 결제 금액: {}원\n - 픽업 시간: {}\n\n - 주문 상태: {}".format(
                            order.userInstance.name,
                            order.storeInstance.name, 
                            order.menuInstance.name, 
                            order.menuInstance.price, 
                            order.pickupTime,
                            order.status
                        ),
                        thumbnail, buttons
                    )

    else:
        KakaoForm = Kakao_SimpleForm()
        KakaoForm.SimpleForm_Init()

        ORDER_LIST_QUICKREPLIES_MAP.append({'action': "message", 'label': "주문 하기",    'messageText': "주문 시간 선택", 'blockid': "none", 'extra': { KAKAO_PARAM_STATUS: KAKAO_PARAM_STATUS_OK }})
        
        if status == NOT_APPLICABLE:
            KakaoForm.SimpleText_Add("주문 내역이 존재하지 않습니다!\n주문하시려면 아래 [주문 하기]를 눌러주세요!")
        else:
            KakaoForm.SimpleText_Add("현재 이용가능한 식권이 없습니다!\n주문하시려면 아래 [주문 하기]를 눌러주세요!")



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

        KakaoForm = Kakao_CarouselForm()
        KakaoForm.BasicCard_Init()

        return JsonResponse(KakaoForm.GetForm())

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

        return OrderListup(ORDER_SUPER_USER_NAME, ORDER_STATUS[ORDER_STATUS_DICT['픽업 준비중']][0])

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
