from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from .models import Store, Menu

import json


class KakaoBaseForm():
    def __init__(self, _version="2.0", _template={"outputs": []}, _context={"values": []}, _data={"Status": 'OK'}):
        self.version  = _version
        self.template = _template
        self.context  = _context
        self.data     = _data

        self.UpdateForm()

    def __new__(cls):
        print('Kaka form new created.')
        return super().__new__(cls)

    def UpdateForm(self):
        self.baseForm = {
            "version":  self.version,
            "template": self.template,
            "context":  self.context,
            "data":     self.data,
        }

    def GetForm(self):
        return self.baseForm

    def SetTemplateForm(self, _template):
        self.template = _template
        self.UpdateForm()

    def SetContextForm(self, _context):
        self.context = _context
        self.UpdateForm()

    def SetDataForm(self, _data):
        self.data = _data
        self.UpdateForm()
        
class Kakao_CarouselForm(KakaoBaseForm):
    def __init__(self, _type='commerceCard', _items=[]):
        super().__init__()
        self.type     = _type
        self.items    = _items

        self.UpdateTemplateForm()

        super().SetTemplateForm(self.template)

    def __new__(cls):
        print('Kaka carousel form created.')
        return super().__new__(cls)

    def UpdateTemplateForm(self):
        self.template = {
            "outputs": [
                {
                    "carousel": {
                        "type": self.type,
                        "items": self.items
                    }
                }
            ]

        }
        
        super().SetTemplateForm(self.template)

    def ComerceCard_Init(self):
        self.type   = 'commerceCard'
        self.items  = []
        self.UpdateTemplateForm()


    def ComerceCard_AddCard(self, _description, _price, _discount, _currency, _thumbnails, _profile, _buttons):
        self.items += {
            "description": _description,
            "price": _price,
            "discount": _discount,
            "currency": _currency,
            "thumbnails": _thumbnails,
            "profile": _profile,
            "buttons": _buttons
        },

        self.UpdateTemplateForm()


    def BasicCard_Init(self):
        self.type   = 'basicCard'
        self.items  = []
        self.UpdateTemplateForm()

    def BasicCard_AddCard(self, _title, _description, _thumbnails, _buttons):
        self.items += {
            "title": _title,
            "description": _description,
            "thumbnails": _thumbnails,
            "buttons": _buttons
        },

        self.UpdateTemplateForm()

    def GetForm(self):
        return self.baseForm

@csrf_exempt
def storeList(request):
    json_str = ((request.body).decode('utf-8'))
    received_json_data = json.loads(json_str)

#    dataIntent = received_json_data['intent']
#    dataUserRequest = received_json_data['userRequest']
#    dataBot = received_json_data['bot']
    dataAction = received_json_data['action']

    print(dataAction)

    KakaoForm = Kakao_CarouselForm()
    KakaoForm.BasicCard_Init()

    storeList = Store.objects.order_by('-store_name')[:5]
    for store in storeList:
            thumbnails = {
                    "imageUrl": "http://k.kakaocdn.net/dn/83BvP/bl20duRC1Q1/lj3JUcmrzC53YIjNDkqbWK/i_6piz1p.jpg",
                    "link": {
                        "web": "https://store.kakaofriends.com/kr/products/1542"
                    }
                }

            buttons = [
                {
                    "action": "block",
                    "label": "메뉴 보기",
                    "messageText": "메뉴 보기",
                    "extra": {
                        "store_name": store.store_name
                    }
                }
            ]

            KakaoForm.BasicCard_AddCard(store.store_name, '설명', thumbnails, buttons)


    return JsonResponse(KakaoForm.GetForm())

@csrf_exempt
def menuList(request):
    json_str = ((request.body).decode('utf-8'))
    received_json_data = json.loads(json_str)

    #dataUserRequest = received_json_data['userRequest']
    #dataBot = received_json_data['bot']
    dataAction = received_json_data['action']

    store = Store.objects.get(store_name=dataAction['clientExtra']['store_name'])

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

        KakaoForm.ComerceCard_AddCard(menu.menu_name, menu.menu_price, 0, 'won', thumbnails, profile, buttons)


    return JsonResponse(KakaoForm.GetForm())


def answer(request):

    json_str = ((request.body).decode('utf-8'))
    received_json_data = json.loads(json_str)
    datacontent = received_json_data['content']

    if datacontent == '버튼1':
        button1 = "버튼1을 누르셨습니다."

        return JsonResponse({
            'message': {
                'text': button1
            },
            'keyboard': {
                'type': 'buttons',
                'buttons': ['버튼1', '버튼2']
            }

        })

    elif datacontent == '버튼2':
        button2 = "버튼2을 누르셨습니다."

        return JsonResponse({
            'message': {
                'text': button2
            },
            'keyboard': {
                'type': 'buttons',
                'buttons': ['버튼1', '버튼2']
            }

        })






