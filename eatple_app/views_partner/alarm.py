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
from eatple_app.define import EP_define
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
            "오늘 잇플에 준비해주실 음식은 {:d}개입니다. \n맛있는 음식 기대할게요!".format(15), "", thumbnail, buttons)

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

        KakaoForm.BasicCard_Add("오늘 잇플 서비스가 모두 종료되었습니다.\n내일 더 맛있는 음식으로 찾아뵐께요!",
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

        KakaoForm.BasicCard_Add("오늘은 11시 30분부터 손님들이 오실예정이에요.\n조금만 서둘러주세요.".format(11),
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

        KakaoForm.BasicCard_Add("오늘은 {}부터 손님들이 오실예정이에요.\n픽업시간에 맞춰 맛있는 음식 준비해주세요.".format("11:55"),
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

        KakaoForm.BasicCard_Add("픽업시간이 다가왔어요. 5분뒤에 손님들이 오실예정이에요.\n반갑게 맞이해주세요.".format(11, 45, 15),
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
