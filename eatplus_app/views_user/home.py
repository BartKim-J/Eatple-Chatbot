'''
    Author : Ben Kim

    @NOTE
    @BUG
    @TODO
 
'''
# System
from eatplus_app.define import EP_define
from eatplus_app.views_user.wording import wordings
from eatplus_app.views_system.debugger import EatplusSkillLog, errorView
from eatplus_app.module_kakao.RequestForm import getLatLng, KakaoPayLoad
from eatplus_app.module_kakao.ReponseForm import Kakao_SimpleForm, Kakao_CarouselForm
from eatplus_app.models import Store, Menu
from eatplus_app.models import Category, SubCategory
from eatplus_app.models import Order, OrderManager
from eatplus_app.models import User
from random import *
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

# Static Functions


def registerUser(userIdentifier):
    userInstance = User.registerUser(
        "잇플 유저 {}".format(randint(1, 10000)), userIdentifier)

    return userInstance


# Viewset
'''
    @name GET_UserHomes
    @param userID

    @note
    @bug
    @todo
'''
@csrf_exempt
def GET_UserHome(request):
    EatplusSkillLog("Home")

    HOME_BTN_MAP = [
        {'action': "message", 'label': wordings.ORDER_BTN,
            'messageText': wordings.GET_SELLING_TIEM_COMMAND, 'blockid': "none", 'extra': {}},

        {'action': "message", 'label': wordings.GET_COUPON_COMMAND,
            'messageText': wordings.GET_COUPON_COMMAND,    'blockid': "none", 'extra': {}},

        {'action': "message", 'label': wordings.GET_ORDER_LIST_COMMAND,
            'messageText': wordings.GET_ORDER_LIST_COMMAND,    'blockid': "none", 'extra': {}},

    ]
    HOME_QUICKREPLIES_MAP = [
        {'action': "message", 'label': wordings.CHANGE_LOCATION_BTN,
            'messageText': wordings.CHANGE_LOCATION_COMMAND,    'blockid': "none", 'extra': {}},

        {'action': "message", 'label': wordings.USER_MANUAL_COMMAND,
            'messageText': wordings.USER_MANUAL_COMMAND,    'blockid': "none", 'extra': {}},
    ]

    thumbnail = {"imageUrl": ""}

    buttons = HOME_BTN_MAP

    try:
        kakaoPayload = KakaoPayLoad(request)

        try:
            userInstance = User.objects.get(
                identifier_code=kakaoPayload.userID)
        except User.DoesNotExist:
            userInstance = registerUser(kakaoPayload.userID)

        KakaoForm = Kakao_CarouselForm()
        KakaoForm.BasicCard_Init()

        KakaoForm.BasicCard_Add(wordings.HOME_TITLE_TEXT,
                                wordings.HOME_DESCRIPT_TEXT, thumbnail, buttons)

        for entryPoint in HOME_QUICKREPLIES_MAP:
            KakaoForm.QuickReplies_Add(entryPoint['action'], entryPoint['label'],
                                       entryPoint['messageText'], entryPoint['blockid'], entryPoint['extra'])

        return JsonResponse(KakaoForm.GetForm())

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView("{}".format(ex))
