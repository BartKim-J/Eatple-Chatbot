'''
    Author : Ben Kim

    @NOTE
    @BUG
    @TODO
 
'''
# System
from eatple_app.define import EP_define
from eatple_app.views_user.wording import wordings
from eatple_app.views_system.debugger import EatplusSkillLog, errorView
from eatple_app.module_kakao.RequestForm import getLatLng, KakaoPayLoad
from eatple_app.module_kakao.ReponseForm import Kakao_SimpleForm, Kakao_CarouselForm
from eatple_app.models import UserIntro
from eatple_app.models import UserManual
from eatple_app.models import Store, Menu
from eatple_app.models import Category, SubCategory
from eatple_app.models import Order, OrderManager
from eatple_app.models import User
import json
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

# Django Library

# External Library

# Models


# Modules

# View-System

# Wordings

# Define

HOST_URL = EP_define.HOST_URL
NOT_APPLICABLE = EP_define.NOT_APPLICABLE

ORDER_STATUS = EP_define.ORDER_STATUS
ORDER_STATUS_DICT = EP_define.ORDER_STATUS_DICT

KAKAO_PARAM_ORDER_ID = EP_define.KAKAO_PARAM_ORDER_ID
KAKAO_PARAM_STORE_ID = EP_define.KAKAO_PARAM_STORE_ID
KAKAO_PARAM_MENU_ID = EP_define.KAKAO_PARAM_MENU_ID

KAKAO_PARAM_STATUS = EP_define.KAKAO_PARAM_STATUS
KAKAO_PARAM_STATUS_OK = EP_define.KAKAO_PARAM_STATUS_OK
KAKAO_PARAM_STATUS_NOT_OK = EP_define.KAKAO_PARAM_STATUS_NOT_OK


# # # # # # # # # # # # # # # # # # # # # # # # #
#
# Static Functions
#
# # # # # # # # # # # # # # # # # # # # # # # # #

# # # # # # # # # # # # # # # # # # # # # # # # #
#
# External View
#
# # # # # # # # # # # # # # # # # # # # # # # # #
DEFAULT_QUICKREPLIES_MAP = [
    {'action': "message", 'label': wordings.RETURN_HOME_QUICK_REPLISE, 'messageText': wordings.RETURN_HOME_QUICK_REPLISE, 'blockid': "none",
        'extra': {KAKAO_PARAM_STATUS: KAKAO_PARAM_STATUS_OK}},
]
'''
    @name GET_UserManual
    @param name

    @note
    @bug
    @tood
'''
@csrf_exempt
def GET_UserManual(request):
    try:
        kakaoPayload = KakaoPayLoad(request)

        EatplusSkillLog("User Manual Flow")

        KakaoForm = Kakao_CarouselForm()
        KakaoForm.BasicCard_Init()

        buttons = [
            # No Buttons
        ]

        userManuals = UserManual.objects.all()

        for manualPage in userManuals:

            thumbnail = {"imageUrl": "{}{}".format(
                HOST_URL, manualPage.imgURL())}

            KakaoForm.BasicCard_Add(
                manualPage.title, manualPage.description, thumbnail, buttons)

        for entryPoint in DEFAULT_QUICKREPLIES_MAP:
            KakaoForm.QuickReplies_Add(entryPoint['action'], entryPoint['label'],
                                       entryPoint['messageText'], entryPoint['blockid'], entryPoint['extra'])

        return JsonResponse(KakaoForm.GetForm())

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView("{}".format(ex))


'''
    @name GET_UserIntro
    @param name

    @note
    @bug
    @tood
'''
@csrf_exempt
def GET_UserIntro(request):
    try:
        kakaoPayload = KakaoPayLoad(request)

        EatplusSkillLog("Partner Manual Flow")

        KakaoForm = Kakao_CarouselForm()
        KakaoForm.BasicCard_Init()

        buttons = [
            # No Buttons
        ]

        userIntros = UserIntro.objects.all()

        for introPage in userIntros:
            thumbnail = {"imageUrl": "{}{}".format(
                HOST_URL, introPage.imgURL())}

            KakaoForm.BasicCard_Add(
                introPage.title, introPage.description, thumbnail, buttons)

        for entryPoint in DEFAULT_QUICKREPLIES_MAP:
            KakaoForm.QuickReplies_Add(entryPoint['action'], entryPoint['label'],
                                       entryPoint['messageText'], entryPoint['blockid'], entryPoint['extra'])

        return JsonResponse(KakaoForm.GetForm())

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView("{}".format(ex))
