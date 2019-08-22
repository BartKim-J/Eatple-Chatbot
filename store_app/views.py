from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from .models import Store, Menu
from .Module_KakaoForm import Kakao_SimpleForm, Kakao_CarouselForm

import json

@csrf_exempt
def storeList(request):
    print("- - - - - - - - - - - - -\n")
    print("-   Store List Skill.   -")
    print("- - - - - - - - - - - - -\n")

    json_str = ((request.body).decode('utf-8'))
    received_json_data = json.loads(json_str)

#    dataIntent = received_json_data['intent']
#    dataUserRequest = received_json_data['userRequest']
#    dataBot = received_json_data['bot']
#    dataAction = received_json_data['action']

    KakaoForm = Kakao_CarouselForm()
    KakaoForm.BasicCard_Init()

    storeList = Store.objects.order_by('-store_name')[:5]
    for store in storeList:
            thumbnail = {
                    "imageUrl": "http://k.kakaocdn.net/dn/83BvP/bl20duRC1Q1/lj3JUcmrzC53YIjNDkqbWK/i_6piz1p.jpg",
                }

            buttons = [
                {
                    "action": "message",
                    "type": "text",
                    "label": "메뉴보기",
                    "messageText": "메뉴보기",
                    "extra": {
                            "store_name": store.store_name,
                    },
                },
            ]

            KakaoForm.BasicCard_AddCard(store.store_name, store.store_description, thumbnail, buttons)


    return JsonResponse(KakaoForm.GetForm())

def menuCardErrorView():
    KakaoForm = Kakao_SimpleForm()
    KakaoForm.SimpleForm_Init()
    KakaoForm.SimpleText_Add("정상적인 경로가 아닙니다ㅠㅜ")

    return JsonResponse(KakaoForm.GetForm())

def menuCardView(store_name):
    store = Store.objects.get(store_name=store_name)

    KakaoForm = Kakao_CarouselForm()
    KakaoForm.ComerceCard_Init()

    menuList = Menu.objects.filter(store=store)[:3]
    for menu in menuList:
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
            {
                "label": "주문하기",
                "action": "webLink",
                "webLinkUrl": "https://store.kakaofriends.com/kr/products/1542"
            },
            {   
                "label": "공유하기",
                "action": "share"
            }
        ]

        KakaoForm.ComerceCard_AddCard(menu.menu_name, menu.menu_price, menu.menu_discount, 'won', thumbnails, profile, buttons)


    return JsonResponse(KakaoForm.GetForm())
@csrf_exempt
def menuList(request):
    print("- - - - - - - - - - - - -")
    print("-   Menu List Skill.    -")
    print("- - - - - - - - - - - - -")

    json_str = ((request.body).decode('utf-8'))
    received_json_data = json.loads(json_str)

    #dataUserRequest = received_json_data['userRequest']
    #dataBot = received_json_data['bot']
    dataAction = received_json_data['action']

    store_name="N/A"
    
    try:
        store_name=dataAction['clientExtra']['store_name']
    except TypeError:
        print(received_json_data)
        print(dataAction['clientExtra'])
        print("Invalid Store Name")

    print("- - - - - - - - - - - - -")

    if store_name != "N/A":
        return menuCardView(store_name)
    else:
        return menuCardErrorView()






