#Django Library
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

#External Library
import requests
import json

#Models 
from .models_config import Config

from .models_user  import User
from .models_order import Order
from .models_store import Store, Menu, Category, SubCategory

#View Modules
from .module_KakaoForm import Kakao_SimpleForm, Kakao_CarouselForm, KakaoPayLoad

#View
from .views_kakaoTool import getLatLng
from .views_system import EatplusSkillLog, errorView

MENU_LIST_LENGTH      = 10
CATEGORY_LIST_LENGTH  =  5

# # # # # # # # # # # # # # # # # # # # # # # # #
#
# Static View
#
# # # # # # # # # # # # # # # # # # # # # # # # #


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
                "nickname": menu.storeInstance.name
            }
            
            kakaoMapUrl = "https://map.kakao.com/link/map/{},{}".format(menu.storeInstance.name, getLatLng(menu.storeInstance.addr))
            buttons = [
                {'action': "message", 'label': "주문하기",  'messageText': "{} 픽업시간 설정".format(sellingTime), 
                 'extra': {
                    Config.KAKAO_EXTRA_STORE_ID:         menu.storeInstance.id,
                    Config.KAKAO_EXTRA_STORE_NAME:       menu.storeInstance.name, 
                    Config.KAKAO_EXTRA_STORE_ADDR:       menu.storeInstance.addr, 

                    Config.KAKAO_EXTRA_MENU_ID:          menu.id,
                    Config.KAKAO_EXTRA_MENU_NAME:        menu.name, 
                    Config.KAKAO_EXTRA_MENU_PRICE:       menu.price, 
                    Config.KAKAO_EXTRA_MENU_DESCRIPTION: menu.description, 
                    Config.KAKAO_EXTRA_MENU_CATEGORY:    menuCategory, 

                    Config.KAKAO_EXTRA_SELLING_TIME:     sellingTime,  
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

# # # # # # # # # # # # # # # # # # # # # # # # #
#
# External View
#
# # # # # # # # # # # # # # # # # # # # # # # # #
@csrf_exempt
def getSellingTime(request):
    try:
        kakaoPayload = KakaoPayLoad(request)

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
        kakaoPayload = KakaoPayLoad(request)

        EatplusSkillLog("Order Flow", "Select Menu [Category: {}, Selling Time : {}]".format(kakaoPayload.menuCategory, kakaoPayload.sellingTime))

        return MenuListup(kakaoPayload.menuCategory, kakaoPayload.sellingTime, kakaoPayload.location)

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView("Select Menu Error\n- {} ".format(ex))

@csrf_exempt
def getPickupTime(request):
    try:
        kakaoPayload = KakaoPayLoad(request)

        EatplusSkillLog("Order Flow", "Get Picktime")

        KakaoForm = Kakao_SimpleForm()
        KakaoForm.SimpleForm_Init()

        KakaoForm.SimpleText_Add("픽업시간이 설정되었습니다!\n결제하기 전에 아래 주문 내역을 확인해주세요.")
        KakaoForm.SimpleText_Add(
            "{}\n - 메뉴: {}\n - 픽업 시간: {}\n\n - 결제 금액: {}원".format(
            kakaoPayload.storeName, kakaoPayload.menuName, kakaoPayload.pickupTime, kakaoPayload.menuPrice)
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
        kakaoPayload = KakaoPayLoad(request)

        EatplusSkillLog("Order Flow", "Order Confirm")

        #@TODO: UserInstance Load User
        pushedOrder = Order.pushOrder(userInstance=User.objects.get(name="잇플"),
                                      storeInstance=Store.objects.get(id=kakaoPayload.storeID), 
                                      menuInstance=Menu.objects.get(id=kakaoPayload.menuID))
        
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
            "주문번호: {}\n--------------------\n - 주문자: {}\n\n - 매장: {} \n - 메뉴: {}\n\n - 결제 금액: {}원\n\n - 픽업 시간: {}\n--------------------\n - 매장 위치: {}".format(
                pushedOrder.management_code,
                pushedOrder.userInstance.name,
                pushedOrder.storeInstance.name, 
                pushedOrder.menuInstance.name, 
                pushedOrder.menuInstance.price, 
                kakaoPayload.pickupTime, 
                pushedOrder.storeInstance.addr
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



