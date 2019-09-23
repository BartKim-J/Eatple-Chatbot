'''
    Author : Ben Kim

    @NOTE
    @BUG
    @TODO
 
'''
#System
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

#Django Library
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

#External Library
import requests
import json
from random import *

#Models 
from eatplus_app.models import User
from eatplus_app.models import Order, OrderManager
from eatplus_app.models import Category, SubCategory
from eatplus_app.models import Store, Menu

#Modules
from eatplus_app.module_kakao.ReponseForm import Kakao_SimpleForm, Kakao_CarouselForm
from eatplus_app.module_kakao.RequestForm import getLatLng, KakaoPayLoad

#View-System
from eatplus_app.views_system.debugger import EatplusSkillLog, errorView

#Wordings
from eatplus_app.views_user.wording import wordings

#Define
from eatplus_app.define import EP_define

#Static Functions
def registerUser(userIdentifier):
    userInstance = User.registerUser("잇플 유저 {}".format(randint(1,10000)), userIdentifier)
    
    return userInstance
 
#Viewset
@csrf_exempt
def userHome(request):
    EatplusSkillLog("Home")

    HOME_BTN_MAP = [
        {'action': "message", 'label': wordings.ORDER_BTN,      'messageText': wordings.GET_SELLING_TIEM_COMMAND, 'blockid': "none", 'extra': {}},

        {'action': "message", 'label': wordings.GET_COUPON_COMMAND, 'messageText': wordings.GET_COUPON_COMMAND,    'blockid': "none", 'extra': {}},

        {'action': "message", 'label': wordings.GET_ORDER_LIST_COMMAND,  'messageText': wordings.GET_ORDER_LIST_COMMAND,    'blockid': "none", 'extra': {}},

    ]
    HOME_QUICKREPLIES_MAP = [
        {'action': "message", 'label': wordings.CHANGE_LOCATION_BTN,      'messageText': wordings.CHANGE_LOCATION_COMMAND,    'blockid': "none", 'extra': {}},

        {'action': "message", 'label': wordings.USER_MANUAL_COMMAND,      'messageText': wordings.USER_MANUAL_COMMAND,    'blockid': "none", 'extra': {}},
    ]

    thumbnail = {"imageUrl": ""}
    
    buttons = HOME_BTN_MAP

    try:
        kakaoPayload = KakaoPayLoad(request)

        userInstance = User.objects.filter(identifier_code=kakaoPayload.userID)

        if not userInstance.exists():
            userInstance = registerUser(kakaoPayload.userID)
            
        KakaoForm = Kakao_CarouselForm()
        KakaoForm.BasicCard_Init()

        KakaoForm.BasicCard_Add(wordings.HOME_TITLE_TEXT, wordings.HOME_DESCRIPT_TEXT, thumbnail, buttons)

        for entryPoint in HOME_QUICKREPLIES_MAP:
            KakaoForm.QuickReplies_Add(entryPoint['action'], entryPoint['label'], entryPoint['messageText'], entryPoint['blockid'], entryPoint['extra'])

        return JsonResponse(KakaoForm.GetForm())

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView("{}".format(ex))


