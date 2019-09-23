#Django Library
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

#External Library
import json
from random import *

#Models 
from eatplus_app.define import EP_define

from eatplus_app.models import User
from eatplus_app.models import Order
from eatplus_app.models import Category, SubCategory
from eatplus_app.models import Store, Menu

#View Modules
from eatplus_app.module_kakao.ReponseForm import Kakao_SimpleForm, Kakao_CarouselForm
from eatplus_app.module_kakao.RequestForm import getLatLng, KakaoPayLoad

#View
#from eatplus_app.views_user import wordings
from eatplus_app.views_system.debugger import EatplusSkillLog, errorView

@csrf_exempt
def partnerHome(request):
    EatplusSkillLog("Home")

    HOME_QUICKREPLIES_MAP = [
        {'action': "message", 'label': "주문 조회",    'messageText': "주문 조회", 'blockid': "none", 'extra': { 'Status': "OK" }},
        {'action': "message", 'label': "정산 조회",    'messageText': "정산 조회", 'blockid': "none", 'extra': { 'Status': "OK" }},
    ]

    try:
        KakaoForm = Kakao_SimpleForm()
        KakaoForm.SimpleForm_Init()

        KakaoForm.SimpleText_Add("잇플 파트너 홈 화면입니다! 아래 명령어 중에 골라주세요!")

        for entryPoint in HOME_QUICKREPLIES_MAP:
            KakaoForm.QuickReplies_Add(entryPoint['action'], entryPoint['label'], entryPoint['messageText'], entryPoint['blockid'], entryPoint['extra'])

        return JsonResponse(KakaoForm.GetForm())

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView("{}".format(ex))


