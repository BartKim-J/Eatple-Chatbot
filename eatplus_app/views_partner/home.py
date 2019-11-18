'''
    Author : Ben Kim

    @NOTE
    @BUG
    @TODO
 
'''
#Django Library
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

#External Library
import json
from random import *

#Models 
from eatplus_app.models import Partner
from eatplus_app.models import Order
from eatplus_app.models import Category, SubCategory
from eatplus_app.models import Store, Menu

#View Modules
from eatplus_app.module_kakao.ReponseForm import Kakao_SimpleForm, Kakao_CarouselForm
from eatplus_app.module_kakao.RequestForm import getLatLng, KakaoPayLoad

#View
from eatplus_app.views_partner.wording import wordings
from eatplus_app.views_system.debugger import EatplusSkillLog, errorView

#Define
from eatplus_app.define import EP_define

DEFAULT_STORE_ID = 28 # Eatple Store Unique ID : 28

#Static Functions
def registerPartner(partnerIdentifier, storeKey):
    partnerInstance = Partner.registerPartner("잇플 파트너 {}".format(randint(1,10000)), partnerIdentifier, storeKey)
    
    return partnerInstance

#Viewset
'''
    @name GET_PartnerHome
    @param userID

    @note
    @bug
    @todo
'''
@csrf_exempt
def GET_PartnerHome(request):
    EatplusSkillLog("Home")

    HOME_BTN_MAP = [
        {'action': "message", 'label': wordings.GET_ORDER_LIST_TOTAL_COMMAND, 'messageText': wordings.GET_ORDER_LIST_TOTAL_COMMAND, 'blockid': "none", 'extra': { 'Status': "OK" }},
        {'action': "message", 'label': wordings.GET_CALCULATE_CHECK_COMMAND, 'messageText': wordings.GET_CALCULATE_CHECK_COMMAND, 'blockid': "none", 'extra': { 'Status': "OK" }},
    ]

    HOME_QUICKREPLIES_MAP = [
        {'action': "message", 'label': wordings.STORE_MANUAL_COMMAND,      'messageText': wordings.STORE_MANUAL_COMMAND,    'blockid': "none", 'extra': {}},
    ]

    try:
        kakaoPayload = KakaoPayLoad(request)

        try:
            partnerInstance = Partner.objects.get(identifier_code=kakaoPayload.userID)
        except Partner.DoesNotExist:
            storeKey = DEFAULT_STORE_ID
            partnerInstance = registerPartner(kakaoPayload.userID, "{}".format(storeKey))
            if (partnerInstance == None):
                return errorView("partner register failed.")
            
            
            
        print(partnerInstance.storeInstance)
            
        KakaoForm = Kakao_CarouselForm()
        KakaoForm.BasicCard_Init()

        thumbnail = {"imageUrl": ""}
        
        buttons = HOME_BTN_MAP
        
        KakaoForm.BasicCard_Add(wordings.HOME_TITLE_TEXT, wordings.HOME_DESCRIPT_TEXT, thumbnail, buttons)

        for entryPoint in HOME_QUICKREPLIES_MAP:
            KakaoForm.QuickReplies_Add(entryPoint['action'], entryPoint['label'], entryPoint['messageText'], entryPoint['blockid'], entryPoint['extra'])

        return JsonResponse(KakaoForm.GetForm())

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView("{}".format(ex))


