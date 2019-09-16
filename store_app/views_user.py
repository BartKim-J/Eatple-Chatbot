#Django Library
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

#External Library
import json

#Models 
from .models_config import Config

from .models_user  import User
from .models_order import Order, OrderManager
from .models_store import Store, Menu, Category, SubCategory

#View Modules
from .module_KakaoForm import Kakao_SimpleForm, Kakao_CarouselForm

from .views_system import EatplusSkillLog, errorView
from .views_wording import wordings

KAKAO_PARAM_USER_ID         = Config.KAKAO_PARAM_USER_ID

ORDER_SUPER_USER_ID         = Config.DEFAULT_USER_ID

@csrf_exempt
def userHome(request):
    EatplusSkillLog("Home")

    HOME_QUICKREPLIES_MAP = [
        {'action': "message", 'label': "주문하기",      'messageText': wordings.GET_SELLING_TIEM_COMMAND, 'blockid': "none", 
        'extra': { KAKAO_PARAM_USER_ID: ORDER_SUPER_USER_ID }},

        {'action': "message", 'label': wordings.GET_COUPON_COMMAND, 'messageText': wordings.GET_COUPON_COMMAND,    'blockid': "none", 
        'extra': { KAKAO_PARAM_USER_ID: ORDER_SUPER_USER_ID }},

        {'action': "message", 'label': wordings.GET_ORDER_LIST_COMMAND,  'messageText': wordings.GET_ORDER_LIST_COMMAND,    'blockid': "none", 
        'extra': { KAKAO_PARAM_USER_ID: ORDER_SUPER_USER_ID }},

        {'action': "message", 'label': "위치변경",      'messageText': "위치변경",    'blockid': "none", 
        'extra': { KAKAO_PARAM_USER_ID: ORDER_SUPER_USER_ID }},

        {'action': "message", 'label': wordings.USER_MANUAL_COMMAND,      'messageText': wordings.USER_MANUAL_COMMAND,    'blockid': "none", 
        'extra': { KAKAO_PARAM_USER_ID: ORDER_SUPER_USER_ID }},
    ]

    try:
        KakaoForm = Kakao_SimpleForm()
        KakaoForm.SimpleForm_Init()

        KakaoForm.SimpleText_Add(wordings.HOME_TEXT)


        for entryPoint in HOME_QUICKREPLIES_MAP:
            KakaoForm.QuickReplies_Add(entryPoint['action'], entryPoint['label'], entryPoint['messageText'], entryPoint['blockid'], entryPoint['extra'])

        return JsonResponse(KakaoForm.GetForm())

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView("{}".format(ex))


