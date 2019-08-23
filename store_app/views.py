from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from .models import Store
from .Module_KakaoForm import Kakao_SimpleForm, Kakao_CarouselForm

import json


def errorView():
    KakaoForm = Kakao_SimpleForm()
    KakaoForm.SimpleForm_Init()

    ERROR_QUICKREPLIES_MAP = [
        {'action': "message", 'label': "홈으로 돌아가기",    'messageText': "홈으로 돌아가기", 'blockid': "none", 'extra': { 'Status': "NOT OK" }},
    ]

    for entryPoint in ERROR_QUICKREPLIES_MAP:
        KakaoForm.QuickReplies_Add(entryPoint['action'], entryPoint['label'], entryPoint['messageText'], entryPoint['blockid'], entryPoint['extra'])

    KakaoForm.SimpleText_Add("진행하는 도중 문제가생겼어요ㅠㅜ")

    return JsonResponse(KakaoForm.GetForm())

def storeView(store_category, menu_category, location):
    KakaoForm = Kakao_CarouselForm()
    KakaoForm.ComerceCard_Init()

    STORE_CATEGORY_QUICKREPLIES_MAP = [
        {'action': "message", 'label': "한식",    'messageText': "메뉴 보기", 'blockid': "none", 'extra': { 'storeCategory': store_category, 'menuCategory': menu_category, }},
        {'action': "message", 'label': "양식",    'messageText': "메뉴 보기", 'blockid': "none", 'extra': { 'storeCategory': store_category, 'menuCategory': menu_category, }},
        {'action': "message", 'label': "중식",    'messageText': "메뉴 보기", 'blockid': "none", 'extra': { 'storeCategory': store_category, 'menuCategory': menu_category, }},
    ]

    for entryPoint in STORE_CATEGORY_QUICKREPLIES_MAP:
        KakaoForm.QuickReplies_Add(entryPoint['action'], entryPoint['label'], entryPoint['messageText'], entryPoint['blockid'], entryPoint['extra'])


    storeList = Store.objects.filter(menu_category=menu_category)[:8]
    for store in storeList:
        thumbnails = [
            {
                "imageUrl": "http://k.kakaocdn.net/dn/83BvP/bl20duRC1Q1/lj3JUcmrzC53YIjNDkqbWK/i_6piz1p.jpg",
                "link": {
                    "web": "https://store.kakaofriends.com/kr/products/1542"
                }
            }
        ]

        
        profile = {
            "imageUrl": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT4BJ9LU4Ikr_EvZLmijfcjzQKMRCJ2bO3A8SVKNuQ78zu2KOqM",
            "nickname": store.store_name
        }
        
        buttons = [
            {'action': "message", 'label': "주문하기",  'messageText': "픽업시간 설정", 'extra': { 'storeCategory': store_category, 'menuCategory': menu_category, }},
            {'action': "webLink", 'label': "지도보기",  "webLinkUrl": "https://map.kakao.com/link/map/18577297"},
        ]

        KakaoForm.ComerceCard_Add(store.menu_name, store.menu_price, store.menu_discount, 'won', thumbnails, profile, buttons)

    return JsonResponse(KakaoForm.GetForm())

### API Functions ###
@csrf_exempt
def home(request):
    print("- - - - - - - - - - - - -")
    print("-     Home Skill.      -")
    print("- - - - - - - - - - - - -")

    HOME_QUICKREPLIES_MAP = [
        {'action': "message", 'label': "주문 하기",    'messageText': "주문시간 선택", 'blockid': "none", 'extra': { 'Status': "OK" }},
        {'action': "message", 'label': "주문 변경",    'messageText': "주문 변경", 'blockid': "none", 'extra': { 'Status': "OK" }},
        {'action': "message", 'label': "픽업시간 변경", 'messageText': "픽업시간 변경", 'blockid': "none", 'extra': { 'Status': "OK" }},
        {'action': "message", 'label': "위치 변경",  'messageText': "위치 변경", 'blockid': "none", 'extra': { 'Status': "OK" }},
    ]

    try:
        KakaoForm = Kakao_SimpleForm()
        KakaoForm.SimpleForm_Init()
        KakaoForm.QuickReplies_Init()

        KakaoForm.SimpleText_Add("홈입니다. 무엇을 하시겠어요?")


        for entryPoint in HOME_QUICKREPLIES_MAP:
            KakaoForm.QuickReplies_Add(entryPoint['action'], entryPoint['label'], entryPoint['messageText'], entryPoint['blockid'], entryPoint['extra'])

        return JsonResponse(KakaoForm.GetForm())

    except (RuntimeError, TypeError, NameError):
        return errorView()
        

@csrf_exempt
def getMenuCategory(request):
    print("- - - - - - - - - - - - -")
    print("-    [ Order Flow ]     -")
    print("-   Get Menu Category   -")
    print("- - - - - - - - - - - - -")


    try:
        json_str = ((request.body).decode('utf-8'))
        received_json_data = json.loads(json_str)

        #dataUserRequest = received_json_data['userRequest']
        #dataBot = received_json_data['bot']
        dataAction = received_json_data['action']

        KakaoForm = Kakao_CarouselForm()
        KakaoForm.BasicCard_Init()

        thumbnail = { "imageUrl": "" }

        buttons = [
            {'action': "message", 'label': "점심",  'messageText': "주문 하기", 'extra': { 'menuCategory': "점심" }},
            {'action': "message", 'label': "저녁",  'messageText': "주문 하기", 'extra': { 'menuCategory': "저녁" }}
        ]

        KakaoForm.BasicCard_Add("점심 또는 저녁을 선택해 주세요!", "", thumbnail, buttons)
    
        return JsonResponse(KakaoForm.GetForm())

    except (RuntimeError, TypeError, NameError):
        return errorView()

@csrf_exempt
def ordering(request):
    print("- - - - - - - - - - - - -")
    print("-    [ Order Flow ]     -")
    print("-      Ordering         -")
    print("- - - - - - - - - - - - -")

    try:
        json_str = ((request.body).decode('utf-8'))
        received_json_data = json.loads(json_str)

        #dataUserRequest = received_json_data['userRequest']
        #dataBot = received_json_data['bot']
        dataAction = received_json_data['action']

        store_category = "N/A"
        menu_category  = dataAction['clientExtra']['menuCategory']
        location       = "N/A"

        return storeView(store_category, menu_category, location)

    except (RuntimeError, TypeError, NameError):
        return JsonResponse(errorView())

@csrf_exempt
def getPickupTime(request):
    print("- - - - - - - - - - - - -")
    print("-    [ Order Flow ]     -")
    print("-   Get Pickup Time     -")
    print("- - - - - - - - - - - - -")

    try:
        json_str = ((request.body).decode('utf-8'))
        received_json_data = json.loads(json_str)

        #dataUserRequest = received_json_data['userRequest']
        #dataBot = received_json_data['bot']
        dataAction = received_json_data['action']

        menu_category = dataAction['clientExtra']['menuCategory']
        location      = "N/A"


        return storeView(menu_category, location)

    except (RuntimeError, TypeError, NameError):
        return errorView()






