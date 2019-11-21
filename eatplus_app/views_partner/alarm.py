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

'''
    @name GET_OpenStoreAlarm
    @param userID

    @note
    @bug
    @tood
'''
@csrf_exempt
def GET_OpenLunchStoreAlarm(request):
    EatplusSkillLog("Open Store Alarm")
    try:
        kakaoPayload = KakaoPayLoad(request)

        KakaoForm = Kakao_CarouselForm()
        KakaoForm.BasicCard_Init()

        thumbnail = {"imageUrl": ""}

        buttons = HOME_BTN_MAP

        KakaoForm.BasicCard_Add(
            "총 {:d}개의 주문이 들어왔어요!", wordings.HOME_DESCRIPT_TEXT, thumbnail, buttons)

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
    EatplusSkillLog("Close Store Alarm")
    try:
        kakaoPayload = KakaoPayLoad(request)

        KakaoForm = Kakao_CarouselForm()
        KakaoForm.BasicCard_Init()

        thumbnail = {"imageUrl": ""}

        buttons = HOME_BTN_MAP

        KakaoForm.BasicCard_Add("오늘의 점심은 마감되었어요!. 다음 저녁 준비를 해주세요!",
                                wordings.HOME_DESCRIPT_TEXT, thumbnail, buttons)

        return JsonResponse(KakaoForm.GetForm())

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView("{} ".format(ex))
