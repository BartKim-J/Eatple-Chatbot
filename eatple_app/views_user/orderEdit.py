'''
    Author : Ben Kim

    @NOTE
    @BUG
    @TODO
 
'''
# System
import sys
import os

# Django Library
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

# External Library
import requests
import json

# Models
from eatple_app.models import User
from eatple_app.models import Order, OrderManager
from eatple_app.models import Category, Tag
from eatple_app.models import Store, Menu

# Modules
from eatple_app.module_kakao.ReponseForm import Kakao_SimpleForm, Kakao_CarouselForm
from eatple_app.module_kakao.RequestForm import getLatLng, KakaoPayLoad

# View-System
from eatple_app.views_system.debugger import EatplusSkillLog, errorView

# Wordings
from eatple_app.views_user.wording import wordings

# Define
from eatple_app.define import *

DEFAULT_QUICKREPLIES_MAP = [
    {'action': "message", 'label': wordings.RETURN_HOME_QUICK_REPLISE,    'messageText': wordings.RETURN_HOME_QUICK_REPLISE, 'blockId': "none",
        'extra': {}},
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
'''
    @name GET_PickupTimeForChange
    @param orderID, sellingTime

    @note
    @bug
    @tood
'''
@csrf_exempt
def GET_PickupTimeForChange(request):
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

        allExtraData = kakaoPayload.dataActionExtra

        PICKUP_TIME_QUICKREPLIES_MAP = []

        if SELLING_TIME_CATEGORY_DICT[kakaoPayload.sellingTime] == SELLING_TIME_LUNCH:
            ENTRY_PICKUP_TIME_MAP = LUNCH_PICKUP_TIME
            pikcupTime_Start = orderInstance.storeInstance.lunch_pickupTime_start
            pikcupTime_End = orderInstance.storeInstance.lunch_pickupTime_end
        else:
            ENTRY_PICKUP_TIME_MAP = DINNER_PICKUP_TIME
            pikcupTime_Start = orderInstance.storeInstance.dinner_pickupTime_start
            pikcupTime_End = orderInstance.storeInstance.dinner_pickupTime_end

        for index, pickupTime in ENTRY_PICKUP_TIME_MAP:
            if(pikcupTime_Start <= index) and (index <= pikcupTime_End):
                PICKUP_TIME_QUICKREPLIES_MAP += {'action': "message", 'label': pickupTime, 'messageText': wordings.ORDER_PICKUP_TIME_CHANGE_CONFIRM_COMMAND,
                                                 'blockId': "none", 'extra': {**allExtraData, KAKAO_PARAM_PICKUP_TIME: pickupTime}},

        for entryPoint in PICKUP_TIME_QUICKREPLIES_MAP:
            KakaoForm.QuickReplies_Add(entryPoint['action'], entryPoint['label'],
                                       entryPoint['messageText'], entryPoint['blockId'], entryPoint['extra'])

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
def SET_PickupTimeByChanged(request):
    try:
        kakaoPayload = KakaoPayLoad(request)

        # Invalied Path Access
        if (kakaoPayload.orderID == NOT_APPLICABLE) or kakaoPayload.pickupTime == NOT_APPLICABLE:
            return errorView("Parameter Invalid")
        else:
            orderInstance = Order.objects.get(id=kakaoPayload.orderID)

        EatplusSkillLog("Order Change Flow")

        beforePickupTime = orderInstance.pickupTime
        orderInstance.pickupTime = orderInstance.rowPickupTimeToDatetime(
            kakaoPayload.pickupTime).replace(day=beforePickupTime.day)
        orderInstance.save()

        KakaoForm = Kakao_CarouselForm()
        KakaoForm.BasicCard_Init()

        thumbnail = {"imageUrl": ""}

        kakaoMapUrl = "https://map.kakao.com/link/map/{},{}".format(
            orderInstance.storeInstance.name, getLatLng(orderInstance.storeInstance.addr))

        buttons = [
            {'action': "webLink", 'label': wordings.SHOW_LOCATION_BTN,
                "webLinkUrl": kakaoMapUrl},
        ]

        KakaoForm.BasicCard_Add(
            "{}시 {}분으로 변경되었습니다.".format(orderInstance.pickupTime.astimezone().strftime(
                '%H'), orderInstance.pickupTime.astimezone().strftime('%M')),
            "주문번호: {}\n--------------------\n - 주문자: {}\n\n - 매장: {} \n - 메뉴: {}\n\n - 결제 금액: {}원\n\n - 픽업 시간: {}\n--------------------".format(
                orderInstance.management_code,
                orderInstance.userInstance.name,
                orderInstance.storeInstance.name,
                orderInstance.menuInstance.name,
                orderInstance.menuInstance.price,
                orderInstance.pickupTime.astimezone().strftime('%H시%M분 %m월%d일'),
            ),
            thumbnail, buttons
        )

        for entryPoint in DEFAULT_QUICKREPLIES_MAP:
            KakaoForm.QuickReplies_Add(entryPoint['action'], entryPoint['label'],
                                       entryPoint['messageText'], entryPoint['blockId'], entryPoint['extra'])

        return JsonResponse(KakaoForm.GetForm())

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView("{}".format(ex))


'''
    @name GET_ConfirmUserCoupon
    @param orderID

    @note
    @bug
    @tood
'''
@csrf_exempt
def GET_ConfirmUserCoupon(request):
    try:
        kakaoPayload = KakaoPayLoad(request)

        # Invalied Path Access
        if(kakaoPayload.orderID == NOT_APPLICABLE):
            return errorView("Parameter Invalid")
        else:
            try:
                userInstance = User.objects.get(
                    identifier_code=kakaoPayload.userID)
            except User.DoesNotExist:
                return errorView("User ID is Invalid")

            OrderInstance = Order.objects.get(id=kakaoPayload.orderID)

        USE_COUPON_QUICKREPLIES_MAP = [
            {'action': "message", 'label': "사용하기",    'messageText': wordings.USE_COUPON_COMMAND,
                'blockId': "none", 'extra': {KAKAO_PARAM_ORDER_ID: OrderInstance.id}},
            {'action': "message", 'label': wordings.RETURN_HOME_QUICK_REPLISE,    'messageText': wordings.RETURN_HOME_QUICK_REPLISE,
                'blockId': "none", 'extra': {}},
        ]

        EatplusSkillLog("Order Check Flow")

        KakaoForm = Kakao_SimpleForm()
        KakaoForm.SimpleForm_Init()

        thumbnail = {"imageUrl": ""}

        buttons = [
            # No Buttons
        ]

        KakaoForm.SimpleText_Add("잇플패스를 사용하시겠습니까?")

        for entryPoint in USE_COUPON_QUICKREPLIES_MAP:
            KakaoForm.QuickReplies_Add(entryPoint['action'], entryPoint['label'],
                                       entryPoint['messageText'], entryPoint['blockId'], entryPoint['extra'])

        return JsonResponse(KakaoForm.GetForm())

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView("{} ".format(ex))


'''
    @name POST_UseCoupon
    @param orderID

    @note
    @bug
    @tood
'''
@csrf_exempt
def POST_UseCoupon(request):
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

        thumbnail = {"imageUrl": ""}

        kakaoMapUrl = "https://map.kakao.com/link/map/{},{}".format(
            orderInstance.storeInstance.name, getLatLng(orderInstance.storeInstance.addr))

        buttons = [
            # No Buttons
        ]

        KakaoForm.BasicCard_Add(
            "잇플패스가 사용되었습니다.",
            "주문번호: {}\n--------------------\n - 주문자: {}\n\n - 매장: {} \n - 메뉴: {}\n\n - 결제 금액: {}원\n\n - 픽업 시간: {}\n--------------------".format(
                orderInstance.management_code,
                orderInstance.userInstance.name,
                orderInstance.storeInstance.name,
                orderInstance.menuInstance.name,
                orderInstance.menuInstance.price,
                orderInstance.pickupTime.astimezone().strftime('%H시%M분 %m월%d일'),
            ),
            thumbnail, buttons
        )

        for entryPoint in DEFAULT_QUICKREPLIES_MAP:
            KakaoForm.QuickReplies_Add(entryPoint['action'], entryPoint['label'],
                                       entryPoint['messageText'], entryPoint['blockId'], entryPoint['extra'])

        return JsonResponse(KakaoForm.GetForm())

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView("{}".format(ex))


'''
    @name POST_OrderCancel
    @param orderID

    @note
    @bug
    @tood
'''
@csrf_exempt
def POST_OrderCancel(request):
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

        thumbnail = {"imageUrl": ""}

        kakaoMapUrl = "https://map.kakao.com/link/map/{},{}".format(
            orderInstance.storeInstance.name, getLatLng(orderInstance.storeInstance.addr))

        buttons = [
            {'action': "webLink", 'label': wordings.SHOW_LOCATION_BTN,
                "webLinkUrl": kakaoMapUrl},
        ]

        KakaoForm.BasicCard_Add(
            "주문이 취소되었습니다. ",
            "주문번호: {}\n--------------------\n - 주문자: {}\n\n - 매장: {} \n - 메뉴: {}\n\n - 결제 금액: {}원\n\n - 픽업 시간: {}\n--------------------".format(
                orderInstance.management_code,
                orderInstance.userInstance.name,
                orderInstance.storeInstance.name,
                orderInstance.menuInstance.name,
                orderInstance.menuInstance.price,
                orderInstance.pickupTime.astimezone().strftime('%H시%M분 %m월%d일'),
            ),
            thumbnail, buttons
        )

        for entryPoint in DEFAULT_QUICKREPLIES_MAP:
            KakaoForm.QuickReplies_Add(entryPoint['action'], entryPoint['label'],
                                       entryPoint['messageText'], entryPoint['blockId'], entryPoint['extra'])

        return JsonResponse(KakaoForm.GetForm())

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView("{} ".format(ex))
