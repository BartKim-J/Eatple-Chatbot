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
from eatple_app.models import Partner
from eatple_app.models import Order, storeOrderManager
from eatple_app.models import Category, Tag
from eatple_app.models import Store, Menu

# Modules
from eatple_app.module_kakao.ReponseForm import Kakao_SimpleForm, Kakao_CarouselForm
from eatple_app.module_kakao.RequestForm import getLatLng, KakaoPayLoad

# View-System
from eatple_app.views_system.debugger import EatplusSkillLog, errorView

# Wordings
from eatple_app.views_partner.wording import wordings

# Define
from eatple_app.define import *

# STATIC EP_define
ORDER_LIST_LENGTH = 30

# # # # # # # # # # # # # # # # # # # # # # # # #
#
# Static View
#
# # # # # # # # # # # # # # # # # # # # # # # # #
'''
    @name StoreOrderListup
    @param storeId

    @note
    @bug
    @todo userName to real username, now just use super user("잇플").
'''


def StoreOrderListup(storeId):
    ORDER_LIST_QUICKREPLIES_MAP = [{'action': "message", 'label': wordings.RETURN_HOME_QUICK_REPLISE, 'messageText': wordings.RETURN_HOME_QUICK_REPLISE, 'blockid': "none", 'extra': {KAKAO_PARAM_STATUS: KAKAO_PARAM_STATUS_OK}},
                                   {'action': "message", 'label': wordings.REFRESH_BTN, 'messageText': wordings.GET_ORDER_LIST_TOTAL_COMMAND, 'blockid': "none", 'extra': {KAKAO_PARAM_STATUS: KAKAO_PARAM_STATUS_OK}}]

    OrderManagerInstance = storeOrderManager(storeId)

    OrderManagerInstance.availableCouponStatusUpdate()

    availableCoupons = OrderManagerInstance.getAvailableCoupons()[
        :ORDER_LIST_LENGTH]

    if availableCoupons:
        KakaoForm = Kakao_CarouselForm()
        KakaoForm.BasicCard_Init()

        for orderInstance in availableCoupons:
            thumbnail = {"imageUrl": ""}

            buttons = [
                # No Buttons
            ]

            KakaoForm.BasicCard_Add(
                "{}".format(orderInstance.menuInstance.name),
                " - 주문자: {}\n\n - 매장: {}\n - 픽업 시간: {}\n\n - 주문 상태: {}".format(
                    orderInstance.userInstance.name,
                    orderInstance.storeInstance.name,
                    orderInstance.pickupTime.astimezone().strftime('%H시%M분 %m월%d일'),
                    orderInstance.status
                ),
                thumbnail, buttons
            )
    else:
        KakaoForm = Kakao_SimpleForm()
        KakaoForm.SimpleForm_Init()

        KakaoForm.SimpleText_Add(wordings.GET_ORDER_LIST_EMPTY_TEXT)

    for entryPoint in ORDER_LIST_QUICKREPLIES_MAP:
        KakaoForm.QuickReplies_Add(entryPoint['action'], entryPoint['label'],
                                   entryPoint['messageText'], entryPoint['blockid'], entryPoint['extra'])

    return JsonResponse(KakaoForm.GetForm())


'''
    @name StoreOrderTotal
    @param storeId

    @note
    @bug
    @tood
'''


def StoreOrderTotal(storeId):
    ORDER_LIST_QUICKREPLIES_MAP = [{'action': "message", 'label': wordings.RETURN_HOME_QUICK_REPLISE, 'messageText': wordings.RETURN_HOME_QUICK_REPLISE, 'blockid': "none", 'extra': {KAKAO_PARAM_STATUS: KAKAO_PARAM_STATUS_OK}},
                                   {'action': "message", 'label': wordings.REFRESH_BTN, 'messageText': wordings.GET_ORDER_LIST_COMMAND, 'blockid': "none", 'extra': {KAKAO_PARAM_STATUS: KAKAO_PARAM_STATUS_OK}}]

    OrderManagerInstance = storeOrderManager(storeId)

    OrderManagerInstance.availableCouponStatusUpdate()

    availableCoupons = OrderManagerInstance.getAvailableCoupons()
    availableCouponTotal = len(availableCoupons)

    if availableCoupons:
        KakaoForm = Kakao_CarouselForm()
        KakaoForm.BasicCard_Init()

        for orderInstance in availableCoupons:
            thumbnail = {"imageUrl": ""}

            buttons = [
                {'action': "message", 'label': wordings.GET_ORDER_LIST_DETAIL_COMMAND, 'messageText': wordings.GET_ORDER_LIST_DETAIL_COMMAND,
                    'blockid': "none", 'extra': {KAKAO_PARAM_STATUS: KAKAO_PARAM_STATUS_OK}}
            ]

            KakaoForm.BasicCard_Add(
                "{}".format(orderInstance.menuInstance.name),
                " - 주문자: {}\n\n - 매장: {}\n - 픽업 시간: {}\n\n - 주문 상태: {}".format(
                    orderInstance.userInstance.name,
                    orderInstance.storeInstance.name,
                    orderInstance.pickupTime.astimezone().strftime('%H시%M분 %m월%d일'),
                    orderInstance.status
                ),
                thumbnail, buttons
            )
    else:
        KakaoForm = Kakao_SimpleForm()
        KakaoForm.SimpleForm_Init()

        KakaoForm.SimpleText_Add(wordings.GET_ORDER_LIST_EMPTY_TEXT)

    for entryPoint in ORDER_LIST_QUICKREPLIES_MAP:
        KakaoForm.QuickReplies_Add(entryPoint['action'], entryPoint['label'],
                                   entryPoint['messageText'], entryPoint['blockid'], entryPoint['extra'])

    return JsonResponse(KakaoForm.GetForm())


# # # # # # # # # # # # # # # # # # # # # # # # #
#
# External View
#
# # # # # # # # # # # # # # # # # # # # # # # # #
'''
    @name GET_StoreOrderList
    @param userID

    @note
    @bug
    @tood
'''
@csrf_exempt
def GET_StoreOrderList(request):
    try:
        kakaoPayload = KakaoPayLoad(request)

        # Invalied Path Access
        if(kakaoPayload.userID == NOT_APPLICABLE):
            return errorView("Parameter Invalid")
        else:
            try:
                partnerInstance = Partner.objects.get(
                    identifier_code=kakaoPayload.userID)
            except Partner.DoesNotExist:
                return errorView("Partner ID is Invalid")

        EatplusSkillLog("Order Check Flow")

        return StoreOrderListup(partnerInstance.storeInstance.id)

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView("{} ".format(ex))


'''
    @name GET_StoreOrderTotal
    @param userID

    @note
    @bug
    @tood
'''
@csrf_exempt
def GET_StoreOrderTotal(request):
    try:
        kakaoPayload = KakaoPayLoad(request)

        # Invalied Path Access
        if(kakaoPayload.userID == NOT_APPLICABLE):
            return errorView("Parameter Invalid")
        else:
            try:
                partnerInstance = Partner.objects.get(
                    identifier_code=kakaoPayload.userID)
            except Partner.DoesNotExist:
                return errorView("Partner ID is Invalid")

        EatplusSkillLog("Order Check Flow")

        return StoreOrderTotal(partnerInstance.storeInstance.id)

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView("{} ".format(ex))
