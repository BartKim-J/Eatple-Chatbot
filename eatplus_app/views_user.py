#Django Library
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

#External Library
import json
from random import *

#Models 
from .eatplus_define import EP_define

from .models_user  import User
from .models_order import Order, OrderManager
from .models_store import Store, Menu, Category, SubCategory

#View Modules
from .module_KakaoForm import Kakao_SimpleForm, Kakao_CarouselForm
from .views_kakaoTool import getLatLng, KakaoPayLoad
from .views_system import EatplusSkillLog, errorView
from .views_wording import wordings


def registerUser(userIdentifier):
    userInstance = User.registerUser("잇플 유저 {}".format(randint(1,10000)), userIdentifier)
    
    return userInstance
 
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


