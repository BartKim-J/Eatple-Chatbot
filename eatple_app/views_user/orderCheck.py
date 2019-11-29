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

# STATIC EP_define
ORDER_LIST_LENGTH = 5


def CouponListup(userID):
    ORDER_LIST_QUICKREPLIES_MAP = [{'action': "message", 'label': wordings.REFRESH_BTN, 'messageText': wordings.GET_COUPON_COMMAND, 'blockId': "none", 'extra': {KAKAO_PARAM_STATUS: KAKAO_PARAM_STATUS_OK}},
                                   {'action': "message", 'label': wordings.RETURN_HOME_QUICK_REPLISE, 'messageText': wordings.RETURN_HOME_QUICK_REPLISE, 'blockId': "none", 'extra': {KAKAO_PARAM_STATUS: KAKAO_PARAM_STATUS_OK}}, ]

    OrderManagerInstance = OrderManager(userID)

    availableCoupons = OrderManagerInstance.availableCouponStatusUpdate()

    # Listup Conpons
    if availableCoupons:
        KakaoForm = Kakao_CarouselForm()
        KakaoForm.BasicCard_Init()

        for orderInstance in availableCoupons:
            thumbnail = {"imageUrl": ""}

            kakaoMapUrl = "https://map.kakao.com/link/map/{},{}".format(
                orderInstance.storeInstance.name, getLatLng(orderInstance.storeInstance.addr))

            buttons = [
                {'action': "webLink", 'label': wordings.SHOW_LOCATION_BTN,
                    "webLinkUrl": kakaoMapUrl},
            ]

            # CAN EDIT COUPONS
            if ORDER_STATUS_DICT[orderInstance.status] <= ORDER_STATUS_DICT['주문 완료']:
                buttons.append({'action': "message", 'label': wordings.ORDER_CANCEL_COMMAND,  'messageText': wordings.ORDER_CANCEL_COMMAND,
                                'extra': {KAKAO_PARAM_ORDER_ID: orderInstance.id}})
                buttons.append({'action': "message", 'label': wordings.ORDER_PICKUP_TIME_CHANGE_COMMAND,  'messageText': "{} {}".format(orderInstance.menuInstance.sellingTime, wordings.ORDER_PICKUP_TIME_CHANGE_COMMAND),
                                'extra': {KAKAO_PARAM_ORDER_ID: orderInstance.id}})

            # CAN'T EDIT COUPONS
            elif ORDER_STATUS_DICT[orderInstance.status] == ORDER_STATUS_DICT['픽업 가능']:
                buttons.append({'action': "message", 'label': "{}하기".format(wordings.USE_COUPON_COMMAND),  'messageText': wordings.CONFIRM_USE_COUPON_COMMAND,
                                'extra': {KAKAO_PARAM_ORDER_ID: orderInstance.id}})
            elif ORDER_STATUS_DICT[orderInstance.status] == ORDER_STATUS_DICT['픽업 준비중']:
                pass
            else:
                errorView("Invalid Case on order status check by now time.")

            # if CAN CHANGE PICKUP TIME:
            #    buttons.append({'action': "message", 'label': "픽업 시간 변경",  'messageText': "픽업 시간 변경", 'extra': { }})
            KakaoForm.BasicCard_Add(
                "주문번호: {}".format(orderInstance.management_code),
                " - 주문자: {}\n\n - 매장: {} \n - 메뉴: {}\n\n - 결제 금액: {}원\n - 픽업 시간: {}\n\n - 주문 상태: {}".format(
                    orderInstance.userInstance.name,
                    orderInstance.storeInstance.name,
                    orderInstance.menuInstance.name,
                    orderInstance.menuInstance.price,
                    orderInstance.pickupTime.astimezone().strftime('%H시%M분 %m월%d일'),
                    orderInstance.status
                ),
                thumbnail, buttons
            )

    # No Coupons
    else:
        KakaoForm = Kakao_SimpleForm()
        KakaoForm.SimpleForm_Init()

        ORDER_LIST_QUICKREPLIES_MAP.insert(0, {'action': "message", 'label': wordings.ORDER_BTN, 'messageText': wordings.GET_SELLING_TIEM_COMMAND, 'blockId': "none",
                                               'extra': {KAKAO_PARAM_STATUS: KAKAO_PARAM_STATUS_OK}})

        KakaoForm.SimpleText_Add(wordings.GET_COUPON_EMPTY_TEXT)

    for entryPoint in ORDER_LIST_QUICKREPLIES_MAP:
        KakaoForm.QuickReplies_Add(entryPoint['action'], entryPoint['label'],
                                   entryPoint['messageText'], entryPoint['blockId'], entryPoint['extra'])

    return JsonResponse(KakaoForm.GetForm())


'''
    @name OrderListup
    @param userID, order_status

    @note
    @bug
    @todo userName to real username, now just use super user("잇플").
'''


def OrderListup(userID):
    ORDER_LIST_QUICKREPLIES_MAP = [{'action': "message", 'label': wordings.RETURN_HOME_QUICK_REPLISE, 'messageText': wordings.RETURN_HOME_QUICK_REPLISE, 'blockId': "none", 'extra': {KAKAO_PARAM_STATUS: KAKAO_PARAM_STATUS_OK}},
                                   {'action': "message", 'label': wordings.REFRESH_BTN, 'messageText': wordings.GET_ORDER_LIST_COMMAND, 'blockId': "none", 'extra': {KAKAO_PARAM_STATUS: KAKAO_PARAM_STATUS_OK}}]

    OrderManagerInstance = OrderManager(userID)

    unavailableCoupons = OrderManagerInstance.getUnavailableCoupons()[
        :ORDER_LIST_LENGTH]

    if unavailableCoupons:
        KakaoForm = Kakao_CarouselForm()
        KakaoForm.BasicCard_Init()

        for orderInstance in unavailableCoupons:
            thumbnail = {"imageUrl": ""}

            #kakaoMapUrl = "https://map.kakao.com/link/map/{},{}".format(orderInstance.storeInstance.name, getLatLng(orderInstance.storeInstance.addr))

            buttons = [
                #{'action': "webLink", 'label': wordings.SHOW_LOCATION_BTN,  "webLinkUrl": kakaoMapUrl},
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
                        orderInstance.pickupTime.astimezone().strftime('%H시%M분 %m월%d일'),
                        orderInstance.status
                    ),
                    thumbnail, buttons
                )
    else:
        KakaoForm = Kakao_SimpleForm()
        KakaoForm.SimpleForm_Init()

        ORDER_LIST_QUICKREPLIES_MAP.append({'action': "message", 'label': wordings.ORDER_BTN,
                                            'messageText': wordings.GET_SELLING_TIEM_COMMAND, 'blockId': "none", 'extra': {KAKAO_PARAM_STATUS: KAKAO_PARAM_STATUS_OK}})

        KakaoForm.SimpleText_Add(wordings.GET_ORDER_LIST_EMPTY_TEXT)

    for entryPoint in ORDER_LIST_QUICKREPLIES_MAP:
        KakaoForm.QuickReplies_Add(entryPoint['action'], entryPoint['label'],
                                   entryPoint['messageText'], entryPoint['blockId'], entryPoint['extra'])

    return JsonResponse(KakaoForm.GetForm())


'''
    @name GET_OrderList
    @param userID

    @note
    @bug
    @tood
'''
@csrf_exempt
def GET_OrderList(request):
    try:
        kakaoPayload = KakaoPayLoad(request)

        # Invalied Path Access
        if(kakaoPayload.userID == NOT_APPLICABLE):
            return errorView("Parameter Invalid")
        else:
            try:
                userInstance = User.objects.get(
                    identifier_code=kakaoPayload.userID)
            except User.DoesNotExist:
                return errorView("User ID is Invalid")

        EatplusSkillLog("Order Check Flow")

        return OrderListup(kakaoPayload.userID)

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView("{} ".format(ex))


'''
    @name GET_Coupon
    @param userID

    @note
    @bug
    @tood
'''
@csrf_exempt
def GET_Coupon(request):
    try:
        kakaoPayload = KakaoPayLoad(request)

        # Invalied Path Access
        if(kakaoPayload.userID == NOT_APPLICABLE):
            return errorView("Parameter Invalid")
        else:
            try:
                userInstance = User.objects.get(
                    identifier_code=kakaoPayload.userID)
            except User.DoesNotExist:
                return errorView("User ID is Invalid")

        EatplusSkillLog("Order Check Flow")

        return CouponListup(kakaoPayload.userID)

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView("{} ".format(ex))
