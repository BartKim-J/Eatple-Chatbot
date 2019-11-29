'''
    Author : Ben Kim

    @NOTE
    @BUG
    @TODO
 
'''
# System
from eatple_app.define import *
from eatple_app.views_user.wording import wordings
from eatple_app.views_system.debugger import EatplusSkillLog, errorView
from eatple_app.module_kakao.RequestForm import getLatLng, KakaoPayLoad
from eatple_app.module_kakao.ReponseForm import Kakao_SimpleForm, Kakao_CarouselForm
from eatple_app.models import Store, Menu
from eatple_app.models import Category, Tag
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
PARTNER_MANUAL_MAP = [
    {'title': "매장고유번호는 어디서 알 수 있나요?",
        'description': "운영매뉴얼에 스티커로 부착되어 있습니다. 분실 시 상담원에게 문의해주세요."},
    {'title': "주문 조회는 어떻게 해야하나요?", 'description': "매일 점심/저녁 예약완료시간에 주문내역을 자동으로 보내드립니다."},
    {'title': "당일 정산 내역은 언제 보내주시나요?",
        'description': "당일 정산내역은 매일 오후 9시에 자동으로 발송해드립니다."},
    {'title': "정산 조회는 어디서 할 수 있나요?",
        'description': "정산 조회를 클릭하신 후 날짜를 선택해주시면 정산내역 확인이 가능합니다."},
    {'title': "잇플에 궁금한 점이 생겼어요!",
        'description': "문의사항이 있는 경우에는 ‘상담원으로 전환하기’를 누르신 후 카카오톡으로 말씀해주세요."},
]

PARTNER_INTRO_MAP = [
    {'title': "단일메뉴로 효율적인 운영", 'description': "하나의 메뉴만 판매가 가능하며, 매장 상황에 맞춰 메뉴 변경이 가능합니다."},
    {'title': "각 매장에 맞는 메뉴선정", 'description': "직접 가격에 맞는 메뉴선택 또는 새로운 메뉴구성을 해주시면 됩니다."},
    {'title': "포장용기 무상제공", 'description': "잇플과 제휴하시면 고급 포장용기를 무상으로 제공해드립니다."},
    {'title': "새로운 온라인 판매채널 확보",
        'description': "포장 판매로 매장 크기, 회전율과 관계없이 추가 매출이 가능해집니다. 선불 결제시스템으로 노쇼로 인한 영업손실을 방지할 수 있습니다."},
    {'title': "잇플의 성공적인 파트너가 되어주세요!",
        'description': "잇플은 점주님들과 함께 성장하기 위해 끊임없이 노력할 것입니다. 잇플과 함께 추가지출 없이 배로 뛰는 매출을 경험하세요."},
]

DEFAULT_QUICKREPLIES_MAP = [
    {'action': "message", 'label': wordings.RETURN_HOME_QUICK_REPLISE, 'messageText': wordings.RETURN_HOME_QUICK_REPLISE, 'blockId': "none",
        'extra': {}},
]
'''
    @name GET_PartnerManual
    @param name

    @note
    @bug
    @tood
'''
@csrf_exempt
def GET_PartnerManual(request):
    try:
        kakaoPayload = KakaoPayLoad(request)

        EatplusSkillLog("Partner Manual Flow")

        KakaoForm = Kakao_CarouselForm()
        KakaoForm.BasicCard_Init()

        thumbnail = {"imageUrl": "{}{}".format(
            HOST_URL, '/media/STORE_DB/images/default/defaultImg.png')}

        buttons = [
            # No Buttons
        ]

        for entryPoint in PARTNER_MANUAL_MAP:
            KakaoForm.BasicCard_Add(
                entryPoint['title'], entryPoint['description'], thumbnail, buttons)

        for entryPoint in DEFAULT_QUICKREPLIES_MAP:
            KakaoForm.QuickReplies_Add(entryPoint['action'], entryPoint['label'],
                                       entryPoint['messageText'], entryPoint['blockId'], entryPoint['extra'])

        return JsonResponse(KakaoForm.GetForm())

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView("{}".format(ex))


'''
    @name GET_PartnerIntro
    @param name

    @note
    @bug
    @tood
'''
@csrf_exempt
def GET_PartnerIntro(request):
    try:
        kakaoPayload = KakaoPayLoad(request)

        EatplusSkillLog("Partner Manual Flow")

        KakaoForm = Kakao_CarouselForm()
        KakaoForm.BasicCard_Init()

        thumbnail = {"imageUrl": "{}{}".format(
            HOST_URL, '/media/STORE_DB/images/default/defaultImg.png')}

        buttons = [
            # No Buttons
        ]

        for entryPoint in PARTNER_INTRO_MAP:
            KakaoForm.BasicCard_Add(
                entryPoint['title'], entryPoint['description'], thumbnail, buttons)

        for entryPoint in DEFAULT_QUICKREPLIES_MAP:
            KakaoForm.QuickReplies_Add(entryPoint['action'], entryPoint['label'],
                                       entryPoint['messageText'], entryPoint['blockId'], entryPoint['extra'])

        return JsonResponse(KakaoForm.GetForm())

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView("{}".format(ex))
