#Django Library
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

#External Library
import json

#Models
from .models_order import Order
from .models_store import Store, Menu

#View Modules
from .module_KakaoForm import Kakao_SimpleForm, Kakao_CarouselForm

from .views_system import EatplusSkillLog, errorView
from .views_ordering import getSellingTime, selectMenu, getPickupTime, orderConfirm
from .views_orderCheck import getOrderList

### API Functions ###
@csrf_exempt
def home(request):
    EatplusSkillLog("Home", "Main")

    HOME_QUICKREPLIES_MAP = [
        {'action': "message", 'label': "주문 하기",    'messageText': "주문시간 선택", 'blockid': "none", 'extra': { 'Status': "OK" }},
        {'action': "message", 'label': "식권 조회",    'messageText': "식권 조회", 'blockid': "none", 'extra': { 'Status': "OK" }},
        {'action': "message", 'label': "주문 변경",    'messageText': "주문 변경", 'blockid': "none", 'extra': { 'Status': "OK" }},
        {'action': "message", 'label': "픽업시간 변경", 'messageText': "픽업시간 변경", 'blockid': "none", 'extra': { 'Status': "OK" }},
        {'action': "message", 'label': "위치 변경",    'messageText': "위치 변경", 'blockid': "none", 'extra': { 'Status': "OK" }},
    ]

    try:
        KakaoForm = Kakao_SimpleForm()
        KakaoForm.SimpleForm_Init()
        KakaoForm.QuickReplies_Init()

        KakaoForm.SimpleText_Add("잇플 홈 화면입니다! 아래 명령어 중에 골라주세요!")


        for entryPoint in HOME_QUICKREPLIES_MAP:
            KakaoForm.QuickReplies_Add(entryPoint['action'], entryPoint['label'], entryPoint['messageText'], entryPoint['blockid'], entryPoint['extra'])

        return JsonResponse(KakaoForm.GetForm())

    except (RuntimeError, TypeError, NameError):
        return errorView()
        

