'''
    Author : Ben Kim

    @NOTE
    @BUG
    @TODO
 
'''
#System
import sys
import os

#Django Library
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

#External Library
import requests
import json

#Models 
from eatplus_app.models import Partner
from eatplus_app.models import Order, storeOrderManager
from eatplus_app.models import Category, SubCategory
from eatplus_app.models import Store, Menu

#Modules
from eatplus_app.module_kakao.ReponseForm import Kakao_SimpleForm, Kakao_CarouselForm
from eatplus_app.module_kakao.RequestForm import getLatLng, KakaoPayLoad

#View-System
from eatplus_app.views_system.debugger import EatplusSkillLog, errorView

#Wordings
from eatplus_app.views_partner.wording import wordings

#Define
from eatplus_app.define import EP_define

NOT_APPLICABLE              = EP_define.NOT_APPLICABLE

KAKAO_PARAM_STATUS          = EP_define.KAKAO_PARAM_STATUS
KAKAO_PARAM_STATUS_OK       = EP_define.KAKAO_PARAM_STATUS_OK
KAKAO_PARAM_STATUS_NOT_OK   = EP_define.KAKAO_PARAM_STATUS_NOT_OK

#STATIC CONFIG
MENU_LIST_LENGTH            = 5
CATEGORY_LIST_LENGTH        = 5

DEFAULT_QUICKREPLIES_MAP = [                
    {'action': "message", 'label': wordings.RETURN_HOME_QUICK_REPLISE,    'messageText': wordings.RETURN_HOME_QUICK_REPLISE, 'blockid': "none", 
        'extra': { KAKAO_PARAM_STATUS: KAKAO_PARAM_STATUS_OK }},
]

'''
    @name GET_CalculateCheck
    @param userID

    @note
    @bug
    @tood
'''
@csrf_exempt
def GET_CalculateCheck(request):
    try:
        kakaoPayload = KakaoPayLoad(request)

        # Invalied Path Access
        if(kakaoPayload.userID == NOT_APPLICABLE):
            return errorView("Parameter Invalid")
        else:
            try:
                partnerInstance = Partner.objects.get(identifier_code=kakaoPayload.userID)
            except Partner.DoesNotExist:
                return errorView("Partner ID is Invalid")

        EatplusSkillLog("Order Check Flow")

        KakaoForm = Kakao_CarouselForm()
        KakaoForm.BasicCard_Init()

        thumbnail = {"imageUrl": ""}
        
        buttons = [
            #NO BUTTONS
        ]
        
        KakaoForm.BasicCard_Add("정산 조회", "정산 조회를 하려면 아래 명령어를 확인해주세요.", thumbnail, buttons)

        for entryPoint in DEFAULT_QUICKREPLIES_MAP:
            KakaoForm.QuickReplies_Add(entryPoint['action'], entryPoint['label'], entryPoint['messageText'], entryPoint['blockid'], entryPoint['extra'])

        return JsonResponse(KakaoForm.GetForm())

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView("{} ".format(ex))
