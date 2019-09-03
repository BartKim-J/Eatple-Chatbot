#Django Library
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

#External Library
import requests
import json

#Models 
from .models_config import Config

from .models_order import Order
from .models_store import Store, Menu, Category, SubCategory

#View Modules
from .module_KakaoForm import Kakao_SimpleForm, Kakao_CarouselForm

#View
from .views_system import EatplusSkillLog, errorView

MENU_LIST_LENGTH      = 10
CATEGORY_LIST_LENGTH  =  5

# # # # # # # # # # # # # # # # # # # # # # # # #
#
# Static View
#
# # # # # # # # # # # # # # # # # # # # # # # # #
class requestPayLoad:
    def __init__(self, request):
        self.json_str           = ((request.body).decode('utf-8'))
        self.received_json_data = json.loads(self.json_str)

        self.dataUserRequest    = self.received_json_data['userRequest']
        self.dataBot            = self.received_json_data['bot']
        
        self.dataAction         = self.received_json_data['action']
        self.dataActionExtra    = self.dataAction['clientExtra']
        self.dataActionParams   = self.dataAction['detailParams']

        # Get paramter
        try:
            self.storeName       = self.dataActionExtra[Config.KAKAO_EXTRA_STORE_NAME]
            self.storeAddr       = self.dataActionExtra[Config.KAKAO_EXTRA_STORE_ADDR]

            self.menuName        = self.dataActionExtra[Config.KAKAO_EXTRA_MENU_NAME]
            self.menuPrice       = self.dataActionExtra[Config.KAKAO_EXTRA_MENU_PRICE]
            self.menuDescription = self.dataActionExtra[Config.KAKAO_EXTRA_MENU_DESCRIPTION]

        except (RuntimeError, TypeError, NameError, KeyError) as ex:
            self.storeName       = Config.NOT_APPLICABLE
            self.storeAddr       = Config.NOT_APPLICABLE

            self.menuName        = Config.NOT_APPLICABLE
            self.menuPrice       = Config.NOT_APPLICABLE
            self.menuDescription = Config.NOT_APPLICABLE
            pass
            
        try:
            self.menuCategory    = self.dataActionExtra[Config.KAKAO_EXTRA_MENU_CATEGORY]
        except (RuntimeError, TypeError, NameError, KeyError) as ex:
            self.menuCategory    = Config.NOT_APPLICABLE
            pass

        try:
            self.sellingTime     = self.dataActionExtra[Config.KAKAO_EXTRA_SELLING_TIME]
        except (RuntimeError, TypeError, NameError, KeyError) as ex:
            self.sellingTime     = Config.NOT_APPLICABLE
            pass

        try:
            self.pickupTime       = self.dataActionParams[Config.KAKAO_EXTRA_PICKUP_TIME][Config.KAKAO_EXTRA_PICKUP_TIME_VALUE][:5]
            self.dataActionExtra  = {**self.dataActionExtra, **{Config.KAKAO_EXTRA_PICKUP_TIME: self.pickupTime}}
        except (RuntimeError, TypeError, NameError, KeyError) as ex:
            self.pickupTime       = Config.NOT_APPLICABLE
            pass
        try:
            self.pickupTime      = self.dataActionExtra[Config.KAKAO_EXTRA_PICKUP_TIME][:5]
        except (RuntimeError, TypeError, NameError, KeyError) as ex:
            pass
        try:
            self.location        = Config.NOT_APPLICABLE
        except (RuntimeError, TypeError, NameError, KeyError) as ex:
            self.location        = Config.NOT_APPLICABLE 
            pass


def MenuListup(menuCategory, sellingTime, location):
    STORE_CATEGORY_QUICKREPLIES_MAP = [                
        {'action': "message", 'label': "홈",    'messageText': "홈으로 돌아가기", 'blockid': "none", 
         'extra': { Config.KAKAO_EXTRA_STATUS: Config.KAKAO_EXTRA_STATUS_OK }},
        {'action': "message", 'label': "전체",    'messageText': "메뉴 보기", 'blockid': "none", 
         'extra': { Config.KAKAO_EXTRA_MENU_CATEGORY: Config.NOT_APPLICABLE, Config.KAKAO_EXTRA_SELLING_TIME: sellingTime, }},
    ]
    
    CategoryList = Category.objects.all()[:CATEGORY_LIST_LENGTH]
    for category in CategoryList:
        STORE_CATEGORY_QUICKREPLIES_MAP += {'action': "message", 'label': category.name,    'messageText': "메뉴 보기", 'blockid': "none", 
        'extra': { Config.KAKAO_EXTRA_MENU_CATEGORY: category.name, Config.KAKAO_EXTRA_SELLING_TIME: sellingTime, }},

    if menuCategory == Config.NOT_APPLICABLE:
        MenuList     = Menu.objects.filter(sellingTime=sellingTime)[:MENU_LIST_LENGTH]
    else:
        MenuList     = Menu.objects.filter(categories__name=menuCategory, sellingTime=sellingTime)[:MENU_LIST_LENGTH]

    if MenuList:
        KakaoForm = Kakao_CarouselForm()
        KakaoForm.ComerceCard_Init()
        
        #Menu Carousel Card Add 
        for menu in MenuList:
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
                "nickname": menu.store_id.name
            }
            
            kakaoMapUrl = "https://map.kakao.com/link/map/{},{}".format(menu.store_id.name, getLatLng(menu.store_id.addr))
            buttons = [
                {'action': "message", 'label': "주문하기",  'messageText': "{} 픽업시간 설정".format(sellingTime), 
                 'extra': {
                    Config.KAKAO_EXTRA_STORE_NAME: menu.store_id.name, 
                    Config.KAKAO_EXTRA_STORE_ADDR: menu.store_id.addr, 

                    Config.KAKAO_EXTRA_MENU_NAME: menu.name, 
                    Config.KAKAO_EXTRA_MENU_PRICE: menu.price, 
                    Config.KAKAO_EXTRA_MENU_DESCRIPTION: menu.description, 
                    Config.KAKAO_EXTRA_MENU_CATEGORY: menuCategory, 

                    Config.KAKAO_EXTRA_SELLING_TIME: sellingTime,  
                }},

                {'action': "webLink", 'label': "위치보기",  "webLinkUrl": kakaoMapUrl },
            ]

            KakaoForm.ComerceCard_Add(menu.name, menu.price, menu.discount, 'won', thumbnails, profile, buttons)

        #Quick Replise Add
        for entryPoint in STORE_CATEGORY_QUICKREPLIES_MAP:
            KakaoForm.QuickReplies_Add(entryPoint['action'], entryPoint['label'], entryPoint['messageText'], entryPoint['blockid'], entryPoint['extra'])

    else:
        KakaoForm = Kakao_SimpleForm()
        KakaoForm.SimpleForm_Init()

        if menuCategory == Config.NOT_APPLICABLE:
            ORDER_EXIT_QUICKREPLIES_MAP = [
                {'action': "message", 'label': "홈으로 돌아가기",    'messageText': "홈으로 돌아가기", 'blockid': "none", 
                 'extra': { Config.KAKAO_EXTRA_STATUS: Config.KAKAO_EXTRA_STATUS_OK }},

                {'action': "message", 'label': "다른 시간대 확인하기",    'messageText': "주문시간 선택", 'blockid': "none", 
                 'extra': { Config.KAKAO_EXTRA_STATUS: Config.KAKAO_EXTRA_STATUS_OK },},
            ]

            for entryPoint in ORDER_EXIT_QUICKREPLIES_MAP:
                KakaoForm.QuickReplies_Add(entryPoint['action'], entryPoint['label'], entryPoint['messageText'], entryPoint['blockid'], entryPoint['extra'])

            KakaoForm.SimpleText_Add("판매중인 {} 메뉴가 없어요ㅠㅜ".format(sellingTime))
        else:
            KakaoForm = Kakao_SimpleForm()
            KakaoForm.SimpleForm_Init()

            for entryPoint in STORE_CATEGORY_QUICKREPLIES_MAP:
                KakaoForm.QuickReplies_Add(entryPoint['action'], entryPoint['label'], entryPoint['messageText'], entryPoint['blockid'], entryPoint['extra'])

            KakaoForm.SimpleText_Add("판매중인 {} 메뉴가 없네요ㅠㅜ".format(menuCategory))

    kakaoReponseData = { 
        Config.KAKAO_EXTRA_MENU_CATEGORY: category.name, 
        Config.KAKAO_EXTRA_SELLING_TIME:  sellingTime,
        Config.KAKAO_EXTRA_STATUS: Config.KAKAO_EXTRA_STATUS_OK,
    }
    
    KakaoForm.SetDataForm(kakaoReponseData)

    return JsonResponse(KakaoForm.GetForm())

def getLatLng(addr):
    try:
        url = 'https://dapi.kakao.com/v2/local/search/address.json?query='+addr
        headers = {"Authorization": "KakaoAK d62991888c78ec58d809bdc591eb62f6"}
        result = json.loads(str(requests.get(url,headers=headers).text))

        match_first = result['documents'][0]['road_address']

    except (RuntimeError, TypeError, NameError, KeyError, IndexError) as ex:
        return errorView("Get Address Error\n- {} ".format(ex))

    return "{},{}".format(float(match_first['y']),float(match_first['x']))

# # # # # # # # # # # # # # # # # # # # # # # # #
#
# External View
#
# # # # # # # # # # # # # # # # # # # # # # # # #
@csrf_exempt
def getSellingTime(request):
    try:
        kakaoPayload = requestPayLoad(request)

        EatplusSkillLog("Order Flow", "=> Enter Ordering Flow\n-  * Get Menu Category")

        KakaoForm = Kakao_CarouselForm()
        KakaoForm.BasicCard_Init()

        thumbnail = { "imageUrl": "" }

        LUNCH  = Config.MENU_CATEGORY[Config.MENU_LUNCH][0]
        DINNER = Config.MENU_CATEGORY[Config.MENU_DINNER][0]

        buttons = [
            {'action': "message", 'label': LUNCH,  'messageText': "{} 주문 하기".format(LUNCH), 
             'extra': { Config.KAKAO_EXTRA_MENU_CATEGORY: Config.NOT_APPLICABLE, 
                        Config.KAKAO_EXTRA_SELLING_TIME: LUNCH }
            },

            {'action': "message", 'label': DINNER,  'messageText': "{} 주문 하기".format(DINNER), 
             'extra': { Config.KAKAO_EXTRA_MENU_CATEGORY: Config.NOT_APPLICABLE, 
                        Config.KAKAO_EXTRA_SELLING_TIME: DINNER }}
        ]

        KakaoForm.BasicCard_Add("점심 또는 저녁을 선택해 주세요!", " * 픽업 가능 시간대 \n - 점심 11:00 ~ 1:30\n - 저녁 05:30 ~ 9:00", thumbnail, buttons)
    
        return JsonResponse(KakaoForm.GetForm())

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView("Get Selling Time Error\n- {} ".format(ex))

@csrf_exempt
def selectMenu(request):
    try:
        kakaoPayload = requestPayLoad(request)

        EatplusSkillLog("Order Flow", "Select Menu [Category: {}, Selling Time : {}]".format(kakaoPayload.menuCategory, kakaoPayload.sellingTime))

        return MenuListup(kakaoPayload.menuCategory, kakaoPayload.sellingTime, kakaoPayload.location)

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView("Select Menu Error\n- {} ".format(ex))

@csrf_exempt
def getPickupTime(request):
    try:
        kakaoPayload = requestPayLoad(request)

        EatplusSkillLog("Order Flow", "Get Picktime")

        KakaoForm = Kakao_SimpleForm()
        KakaoForm.SimpleForm_Init()

        KakaoForm.SimpleText_Add("픽업시간이 설정되었습니다!\n결제하기 전에 아래 주문 내역을 확인해주세요.")
        KakaoForm.SimpleText_Add(
            " * {}\n-------------------- \n * 메뉴 이름: {}\n * 시간대  : {}\n * 픽업 시간: {} \n--------------------\n * 결제 금액: {}원".format(
            kakaoPayload.storeName, kakaoPayload.menuName, kakaoPayload.sellingTime, kakaoPayload.pickupTime, kakaoPayload.menuPrice)
        )

        ORDER_EXIT_QUICKREPLIES_MAP = [
            {'action': "message", 'label': "결제 하기",    'messageText': "결제 하기", 'blockid': "none", 
            'extra': kakaoPayload.dataActionExtra},

            {'action': "message", 'label': "주문 취소 하기",    'messageText': "주문 취소 하기", 'blockid': "none", 
             'extra': { Config.KAKAO_EXTRA_STATUS: Config.KAKAO_EXTRA_STATUS_OK }},
        ]

        for entryPoint in ORDER_EXIT_QUICKREPLIES_MAP:
            KakaoForm.QuickReplies_Add(entryPoint['action'], entryPoint['label'], entryPoint['messageText'], entryPoint['blockid'], entryPoint['extra'])
        

        return JsonResponse(KakaoForm.GetForm())

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView("Get Pickup Time Error\n- {} ".format(ex))


@csrf_exempt
def orderConfirm(request):
    try:
        kakaoPayload = requestPayLoad(request)

        EatplusSkillLog("Order Flow", "Order Confirm")

        KakaoForm = Kakao_CarouselForm()
        KakaoForm.BasicCard_Init()

        thumbnail = { "imageUrl": "" }

        kakaoMapUrl = "https://map.kakao.com/link/map/{},{}".format(kakaoPayload.storeName, getLatLng(kakaoPayload.storeAddr))

        buttons = [
            {'action': "webLink", 'label': "위치보기",  "webLinkUrl": kakaoMapUrl},
            {'action': "message", 'label': "결제 취소 하기",  'messageText': "결제 취소 하기", 
             'extra': { Config.KAKAO_EXTRA_MENU_CATEGORY: Config.NOT_APPLICABLE }}
        ]

        KakaoForm.BasicCard_Add(
            "식권이 발급되었습니다.",
            "주문번호: {}\n--------------------\n - 매장 이름: {} \n - 메뉴 이름: {}\n - 결제 금액: {}원\n - 픽업 시간: {}\n--------------------\n - 매장 위치: {}".format(
                "ABCDE12345F",
                kakaoPayload.storeName, 
                kakaoPayload.menuName, 
                kakaoPayload.menuPrice, 
                kakaoPayload.pickupTime, 
                kakaoPayload.storeAddr
            ),
            thumbnail, buttons
        )

        ORDER_EXIT_QUICKREPLIES_MAP = [
            {'action': "message", 'label': "홈으로 돌아가기", 'messageText': "홈으로 돌아가기", 'blockid': "none", 
             'extra': { Config.KAKAO_EXTRA_STATUS: Config.KAKAO_EXTRA_STATUS_OK }},
        ]

        for entryPoint in ORDER_EXIT_QUICKREPLIES_MAP:
            KakaoForm.QuickReplies_Add(entryPoint['action'], entryPoint['label'], entryPoint['messageText'], entryPoint['blockid'], entryPoint['extra'])
        

        return JsonResponse(KakaoForm.GetForm())

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView("Get Pickup Time Error\n- {} ".format(ex))



