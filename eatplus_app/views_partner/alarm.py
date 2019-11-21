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
from eatplus_app.models import Partner
from eatplus_app.models import Order, storeOrderManager
from eatplus_app.models import Category, SubCategory
from eatplus_app.models import Store, Menu

# Modules
from eatplus_app.module_kakao.ReponseForm import Kakao_SimpleForm, Kakao_CarouselForm
from eatplus_app.module_kakao.RequestForm import getLatLng, KakaoPayLoad

# View-System
from eatplus_app.views_system.debugger import EatplusSkillLog, errorView

# Wordings
from eatplus_app.views_partner.wording import wordings

# Define
from eatplus_app.define import EP_define
TIME_ZONE = EP_define.TIME_ZONE
NOT_APPLICABLE = EP_define.NOT_APPLICABLE

SELLING_TIME_LUNCH = EP_define.SELLING_TIME_LUNCH
SELLING_TIME_DINNER = EP_define.SELLING_TIME_DINNER
SELLING_TIME_CATEGORY_DICT = EP_define.SELLING_TIME_CATEGORY_DICT
SELLING_TIME_CATEGORY = EP_define.SELLING_TIME_CATEGORY

ORDER_STATUS = EP_define.ORDER_STATUS
ORDER_STATUS_DICT = EP_define.ORDER_STATUS_DICT

KAKAO_PARAM_ORDER_ID = EP_define.KAKAO_PARAM_ORDER_ID
KAKAO_PARAM_STORE_ID = EP_define.KAKAO_PARAM_STORE_ID
KAKAO_PARAM_MENU_ID = EP_define.KAKAO_PARAM_MENU_ID

KAKAO_PARAM_STATUS = EP_define.KAKAO_PARAM_STATUS
KAKAO_PARAM_STATUS_OK = EP_define.KAKAO_PARAM_STATUS_OK
KAKAO_PARAM_STATUS_NOT_OK = EP_define.KAKAO_PARAM_STATUS_NOT_OK

ORDER_SUPER_USER_ID = EP_define.DEFAULT_USER_ID


DEFAULT_QUICKREPLIES_MAP = [
    {'action': "message", 'label': wordings.RETURN_HOME_QUICK_REPLISE,    'messageText': wordings.RETURN_HOME_QUICK_REPLISE, 'blockid': "none",
        'extra': {KAKAO_PARAM_STATUS: KAKAO_PARAM_STATUS_OK}},
]

'''
    @name GET_OpenStoreAlarm
    @param userID

    @note
    @bug
    @tood
'''
@csrf_exempt
def GET_OpenLunchStoreAlarm(request):
    EatplusSkillLog("Open Lunch Store Alarm")
        
    try:
        kakaoPayload = KakaoPayLoad(request)

        KakaoForm = Kakao_CarouselForm()
        KakaoForm.BasicCard_Init()

        thumbnail = {"imageUrl": ""}

        buttons = [
            {'action': "message", 'label': "주문 확인하러 가기",    'messageText': "주문 조회", 'blockid': "none",
             'extra': {KAKAO_PARAM_STATUS: KAKAO_PARAM_STATUS_OK}},
        ]

        KakaoForm.BasicCard_Add(
            "총 {:d}개의 점심 주문이 들어왔어요!".format(15), "", thumbnail, buttons)

        return JsonResponse(KakaoForm.GetForm())

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView("{} ".format(ex))


'''
    @name GET_CloseStoreAlarm
    @param userID

    @note
    @bug
    @tood
'''
@csrf_exempt
def GET_CloseLunchStoreAlarm(request):
    EatplusSkillLog("Close Lunch Store Alarm")

    try:
        kakaoPayload = KakaoPayLoad(request)

        KakaoForm = Kakao_CarouselForm()
        KakaoForm.BasicCard_Init()

        thumbnail = {"imageUrl": ""}

        buttons = DEFAULT_QUICKREPLIES_MAP

        KakaoForm.BasicCard_Add("오늘의 점심은 마감되었어요!. 다음 저녁 준비를 해주세요!",
                                "", thumbnail, buttons)

        return JsonResponse(KakaoForm.GetForm())

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView("{} ".format(ex))
    
'''
    @name GET_OpenDinnerStoreAlarm
    @param userID

    @note
    @bug
    @tood
'''
@csrf_exempt
def GET_OpenDinnerStoreAlarm(request):
    EatplusSkillLog("Close Dinner Store Alarm")

    try:
        kakaoPayload = KakaoPayLoad(request)

        KakaoForm = Kakao_CarouselForm()
        KakaoForm.BasicCard_Init()

        thumbnail = {"imageUrl": ""}

        buttons = [
            {'action': "message", 'label': "주문 확인하러 가기", 'messageText': "주문 조회", 'blockid': "none",
             'extra': {KAKAO_PARAM_STATUS: KAKAO_PARAM_STATUS_OK}},
        ]

        KakaoForm.BasicCard_Add("총 {:d}개의 저녁 주문이 들어왔어요!".format(11),
                                "", thumbnail, buttons)

        return JsonResponse(KakaoForm.GetForm())

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView("{} ".format(ex))


'''
    @name GET_CloseDinnerStoreAlarm
    @param userID

    @note
    @bug
    @tood
'''
@csrf_exempt
def GET_CloseDinnerStoreAlarm(request):
    EatplusSkillLog("Close Dinner Store Alarm")
    
    try:
        kakaoPayload = KakaoPayLoad(request)

        KakaoForm = Kakao_CarouselForm()
        KakaoForm.BasicCard_Init()

        thumbnail = {"imageUrl": ""}

        buttons = DEFAULT_QUICKREPLIES_MAP

        KakaoForm.BasicCard_Add("오늘의 저녁은 마감되었어요!. 오늘 하루 수고하셨습니다.",
                                "", thumbnail, buttons)

        return JsonResponse(KakaoForm.GetForm())

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView("{} ".format(ex))


'''
    @name GET_PickupAlarm
    @param userID

    @note
    @bug
    @tood
'''
@csrf_exempt
def GET_PickupAlarm(request):
    EatplusSkillLog("Close Dinner Store Alarm")
    
    try:
        kakaoPayload = KakaoPayLoad(request)

        KakaoForm = Kakao_CarouselForm()
        KakaoForm.BasicCard_Init()

        thumbnail = {"imageUrl": ""}

        buttons = DEFAULT_QUICKREPLIES_MAP

        KakaoForm.BasicCard_Add("픽업시간({:d} : {:d}) 5분 전 입니다. \n {:d}개를 준비해주세요!".format(11, 45, 15),
                                "", thumbnail, buttons)

        return JsonResponse(KakaoForm.GetForm())

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView("{} ".format(ex))

'''
    @name GET_PickupBlockEnableAlarm
    @param userID

    @note
    @bug
    @tood
'''
@csrf_exempt
def GET_PickupBlockEnableAlarm(request):
    EatplusSkillLog("Close Dinner Store Alarm")
    
    try:
        kakaoPayload = KakaoPayLoad(request)

        KakaoForm = Kakao_CarouselForm()
        KakaoForm.BasicCard_Init()

        thumbnail = {"imageUrl": ""}

        buttons = DEFAULT_QUICKREPLIES_MAP


        KakaoForm.BasicCard_Add("픽업불가 시작 시간입니다.",
                                "", thumbnail, buttons)

        return JsonResponse(KakaoForm.GetForm())

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView("{} ".format(ex))


'''
    @name GET_PickupBlockDisableAlarm
    @param userID

    @note
    @bug
    @tood
'''
@csrf_exempt
def GET_PickupBlockDisableAlarm(request):
    EatplusSkillLog("Close Dinner Store Alarm")

    try:
        kakaoPayload = KakaoPayLoad(request)

        KakaoForm = Kakao_CarouselForm()
        KakaoForm.BasicCard_Init()

        thumbnail = {"imageUrl": ""}

        buttons = DEFAULT_QUICKREPLIES_MAP
        
        KakaoForm.BasicCard_Add("픽업불가 종료 시간입니다.",
                                "", thumbnail, buttons)

        return JsonResponse(KakaoForm.GetForm())

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView("{} ".format(ex))
