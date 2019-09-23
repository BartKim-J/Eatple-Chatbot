#Django Library
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

#External Library
import json


#Models
from .eatplus_define import EP_define

from .models_order import Order
from .models_store import Store, Menu

#View Modules
from .module_KakaoForm import Kakao_SimpleForm, Kakao_CarouselForm

from .views_system import EatplusSkillLog, errorView

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


