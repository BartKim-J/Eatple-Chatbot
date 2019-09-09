#Django Library
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

#External Library
import datetime
import requests
import json

#Models 
from .models_config import Config

from .models_user  import User
from .models_order import Order
from .models_store import Store, Menu, Category, SubCategory

#View Modules
from .module_KakaoForm import Kakao_SimpleForm, Kakao_CarouselForm

#View
from .views_kakaoTool import getLatLng, KakaoPayLoad
from .views_system import EatplusSkillLog, errorView

#GLOBAL DEFINE
NOT_APPLICABLE              = Config.NOT_APPLICABLE

MENU_LUNCH                  = Config.MENU_LUNCH
MENU_DINNER                 = Config.MENU_DINNER
MENU_CATEGORY_DICT          = Config.MENU_CATEGORY_DICT
MENU_CATEGORY               = Config.MENU_CATEGORY

ORDER_STATUS                = Config.ORDER_STATUS
ORDER_STATUS_DICT           = Config.ORDER_STATUS_DICT

KAKAO_PARAM_USER_ID         = Config.KAKAO_PARAM_USER_ID
KAKAO_PARAM_ORDER_ID        = Config.KAKAO_PARAM_ORDER_ID
KAKAO_PARAM_STORE_ID        = Config.KAKAO_PARAM_STORE_ID
KAKAO_PARAM_MENU_ID         = Config.KAKAO_PARAM_MENU_ID

KAKAO_PARAM_MENU_CATEGORY   = Config.KAKAO_PARAM_MENU_CATEGORY
KAKAO_PARAM_SELLING_TIME    = Config.KAKAO_PARAM_SELLING_TIME
KAKAO_PARAM_PICKUP_TIME     = Config.KAKAO_PARAM_PICKUP_TIME

KAKAO_PARAM_STATUS          = Config.KAKAO_PARAM_STATUS
KAKAO_PARAM_STATUS_OK       = Config.KAKAO_PARAM_STATUS_OK
KAKAO_PARAM_STATUS_NOT_OK   = Config.KAKAO_PARAM_STATUS_NOT_OK

#STATIC CONFIG
MENU_LIST_LENGTH      = 10
CATEGORY_LIST_LENGTH  =  5

DEFAULT_QUICKREPLIES_MAP = [                
    {'action': "message", 'label': "홈으로 돌아가기",    'messageText': "홈으로 돌아가기", 'blockid': "none", 
        'extra': { KAKAO_PARAM_STATUS: KAKAO_PARAM_STATUS_OK }},
]

# # # # # # # # # # # # # # # # # # # # # # # # #
#
# Static View
#
# # # # # # # # # # # # # # # # # # # # # # # # #
def MenuListup(menuCategory, sellingTime, location):
    ALL_MENU = '전체'

    STORE_CATEGORY_QUICKREPLIES_MAP = [                
        {'action': "message", 'label': "홈",    'messageText': "홈으로 돌아가기", 'blockid': "none", 
         'extra': { KAKAO_PARAM_STATUS: KAKAO_PARAM_STATUS_OK }},
        {'action': "message", 'label': "전체",    'messageText': "{} {} 메뉴 보기".format(sellingTime, ALL_MENU), 'blockid': "none", 
         'extra': { KAKAO_PARAM_MENU_CATEGORY: NOT_APPLICABLE, KAKAO_PARAM_SELLING_TIME: sellingTime, }},
    ]
    
    CategoryList = Category.objects.all()[:CATEGORY_LIST_LENGTH]
    for category in CategoryList:
        STORE_CATEGORY_QUICKREPLIES_MAP.append({'action': "message", 'label': category.name, 'messageText': "{} {} 메뉴 보기".format(sellingTime, category.name), 'blockid': "none", 
                                                'extra': { KAKAO_PARAM_MENU_CATEGORY: category.name, KAKAO_PARAM_SELLING_TIME: sellingTime }})
        
    if(menuCategory == NOT_APPLICABLE) or (menuCategory == ALL_MENU):
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
                    KAKAO_PARAM_STORE_ID:         menu.storeInstance.id,
                    KAKAO_PARAM_MENU_ID:          menu.id,
                    KAKAO_PARAM_MENU_CATEGORY:    menuCategory, 
                    KAKAO_PARAM_SELLING_TIME:     sellingTime,  
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

        if menuCategory == NOT_APPLICABLE:
            ORDER_EXIT_QUICKREPLIES_MAP = [
                {'action': "message", 'label': "홈으로 돌아가기",    'messageText': "홈으로 돌아가기", 'blockid': "none", 
                 'extra': { KAKAO_PARAM_STATUS: KAKAO_PARAM_STATUS_OK }},

                {'action': "message", 'label': "다른 시간대 확인하기",    'messageText': "주문시간 선택", 'blockid': "none", 
                 'extra': { KAKAO_PARAM_STATUS: KAKAO_PARAM_STATUS_OK }},
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
        KAKAO_PARAM_MENU_CATEGORY: category.name, 
        KAKAO_PARAM_SELLING_TIME:  sellingTime,
        KAKAO_PARAM_STATUS: KAKAO_PARAM_STATUS_OK,
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

        LUNCH  = MENU_CATEGORY[MENU_LUNCH][0]
        DINNER = MENU_CATEGORY[MENU_DINNER][0]

        buttons = [
            {'action': "message", 'label': LUNCH,  'messageText': "{} 주문 하기".format(LUNCH), 
             'extra': { KAKAO_PARAM_MENU_CATEGORY: NOT_APPLICABLE, 
                        KAKAO_PARAM_SELLING_TIME: LUNCH }
            },

            {'action': "message", 'label': DINNER,  'messageText': "{} 주문 하기".format(DINNER), 
             'extra': { KAKAO_PARAM_MENU_CATEGORY: NOT_APPLICABLE, 
                        KAKAO_PARAM_SELLING_TIME: DINNER }}
        ]

        KakaoForm.BasicCard_Add("점심 또는 저녁을 선택해 주세요!", " * 예약 가능 시간대 \n - 점심 : 20:00 ~ 10:30\n - 저녁 : 10:30 ~ 20:00", thumbnail, buttons)
    
        for entryPoint in DEFAULT_QUICKREPLIES_MAP:
            KakaoForm.QuickReplies_Add(entryPoint['action'], entryPoint['label'], entryPoint['messageText'], entryPoint['blockid'], entryPoint['extra'])
        

        return JsonResponse(KakaoForm.GetForm())

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView("Get Selling Time Error\n- {} ".format(ex))

@csrf_exempt
def selectMenu(request):
    try:
        kakaoPayload = KakaoPayLoad(request)

        # Invalied Path Access
        if kakaoPayload.sellingTime == NOT_APPLICABLE: #and (kakaoPayload.menuCategory == NOT_APPLICABLE) => "ALL MENU"
            return errorView("Select Menu -> Parameter Error")
      
        EatplusSkillLog("Order Flow", "Select Menu [Category: {}, Selling Time : {}]".format(kakaoPayload.menuCategory, kakaoPayload.sellingTime))

        return MenuListup(kakaoPayload.menuCategory, kakaoPayload.sellingTime, kakaoPayload.location)

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView("Select Menu Error\n- {} ".format(ex))


@csrf_exempt
def getPickupTime(request):
    try:
        kakaoPayload = KakaoPayLoad(request)

        # Invalied Path Access
        if(kakaoPayload.storeID == NOT_APPLICABLE) or (kakaoPayload.menuID  == NOT_APPLICABLE) or (kakaoPayload.sellingTime == NOT_APPLICABLE):
            return errorView("Get Pickup Time -> Parameter Error\n {} \n {}".format(kakaoPayload.storeID, kakaoPayload.menuID))
        else:
            storeInstance = Store.objects.get(id=kakaoPayload.storeID)
            menuInstance  = Menu.objects.get(id=kakaoPayload.menuID)

        EatplusSkillLog("Order Flow", "Get Picktime")

        KakaoForm = Kakao_SimpleForm()
        KakaoForm.SimpleForm_Init()

        KakaoForm.SimpleText_Add("{} 시간 픽업 시간을 설정해주세요.".format(kakaoPayload.sellingTime))

        PICKUP_TIME_QUICKREPLIES_MAP = []

        LUNCH_PICKUP_TIME_MAP  = [ "11:30", "11:45", "12:00", "12:15", "12:30", "12:45", "13:00", "13:15", "13:30" ]
        DINNER_PICKUP_TIME_MAP = [ "17:30", "18:00", "18:30", "19:00", "19:30", "20:00", "20:30", "21:00" ]
        if MENU_CATEGORY_DICT[kakaoPayload.sellingTime] == MENU_LUNCH:
            ENTRY_PICKUP_TIME_MAP = LUNCH_PICKUP_TIME_MAP
        else:
            ENTRY_PICKUP_TIME_MAP = DINNER_PICKUP_TIME_MAP

        allExtraData = kakaoPayload.dataActionExtra

        for pickupTime in ENTRY_PICKUP_TIME_MAP:
            PICKUP_TIME_QUICKREPLIES_MAP += {'action': "message", 'label': pickupTime, 'messageText': "픽업 시간 설정 완료", 'blockid': "none", 'extra': { **allExtraData, KAKAO_PARAM_PICKUP_TIME: pickupTime}},

        for entryPoint in PICKUP_TIME_QUICKREPLIES_MAP:
            KakaoForm.QuickReplies_Add(entryPoint['action'], entryPoint['label'], entryPoint['messageText'], entryPoint['blockid'], entryPoint['extra'])

        return JsonResponse(KakaoForm.GetForm())

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView("Get Pickup Time Error\n- {} ".format(ex))

@csrf_exempt
def pickupTimeConfirm(request):
    try:
        kakaoPayload = KakaoPayLoad(request)

        # Invalied Path Access
        if(kakaoPayload.storeID == NOT_APPLICABLE) or (kakaoPayload.menuID  == NOT_APPLICABLE) or (kakaoPayload.pickupTime == NOT_APPLICABLE):
            return errorView("Get Pickup Time -> Parameter Error\n {} \n {}".format(kakaoPayload.storeID, kakaoPayload.menuID))
        else:
            storeInstance = Store.objects.get(id=kakaoPayload.storeID)
            menuInstance  = Menu.objects.get(id=kakaoPayload.menuID)

        EatplusSkillLog("Order Flow", "Pickuptime Confirm")
        KakaoForm = Kakao_CarouselForm()
        KakaoForm.ComerceCard_Init()
        
        #Menu Carousel Card Add 
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
            "nickname": menuInstance.storeInstance.name
        }
        
        kakaoMapUrl = "https://map.kakao.com/link/map/{},{}".format(storeInstance.name, getLatLng(storeInstance.addr))
        buttons = [
            {'action': "message", 'label': "결제 하기",  'messageText': "결제 하기", 'extra': kakaoPayload.dataActionExtra},
        ]

        KakaoForm.ComerceCard_Add("메뉴명     : {}\n픽업 시간 : {}".format(menuInstance.name, kakaoPayload.pickupTime), 
                                   menuInstance.price, menuInstance.discount, 'won', thumbnails, profile, buttons)

        GET_PICKUP_TIME_QUICKREPLIES_MAP = [
            {'action': "message", 'label': "픽업시간 변경하기",  'messageText': "{} 픽업시간 설정".format(kakaoPayload.sellingTime), 'blockid': "none", 'extra': kakaoPayload.dataActionExtra},
            {'action': "message", 'label': "취소 하기",        'messageText': "취소 하기", 'blockid': "none", 'extra': { KAKAO_PARAM_STATUS: KAKAO_PARAM_STATUS_OK }},
        ]

        for entryPoint in GET_PICKUP_TIME_QUICKREPLIES_MAP:
            KakaoForm.QuickReplies_Add(entryPoint['action'], entryPoint['label'], entryPoint['messageText'], entryPoint['blockid'], entryPoint['extra'])

        return JsonResponse(KakaoForm.GetForm())

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView("Pickuptime Confirm Error\n- {} ".format(ex))


@csrf_exempt
def orderConfirm(request):
    try:
        kakaoPayload = KakaoPayLoad(request)

        # Invalied Path Access
        if(kakaoPayload.storeID == NOT_APPLICABLE) and (kakaoPayload.menuID  == NOT_APPLICABLE) and (kakaoPayload.pickupTime == NOT_APPLICABLE):
            return errorView("Order Confirm Time -> Parameter Error")
        else:
            storeInstance = Store.objects.get(id=kakaoPayload.storeID)
            menuInstance  = Menu.objects.get(id=kakaoPayload.menuID)

        EatplusSkillLog("Order Flow", "Order Confirm")

        #@TODO: UserInstance Load User
        pushedOrder = Order.pushOrder(userInstance=User.objects.get(name="잇플"),
                                      storeInstance=Store.objects.get(id=kakaoPayload.storeID), 
                                      menuInstance=Menu.objects.get(id=kakaoPayload.menuID),
                                      pickupTime=kakaoPayload.pickupTime)
        
        KakaoForm = Kakao_CarouselForm()
        KakaoForm.BasicCard_Init()

        thumbnail = { "imageUrl": "" }

        kakaoMapUrl = "https://map.kakao.com/link/map/{},{}".format(storeInstance.name, getLatLng(storeInstance.addr))

        buttons = [
            {'action': "webLink", 'label': "위치보기",  "webLinkUrl": kakaoMapUrl},
            {'action': "message", 'label': "주문 취소 하기",  'messageText': "주문 취소 하기", 
             'extra': { KAKAO_PARAM_ORDER_ID: pushedOrder.id }}
        ]

        KakaoForm.BasicCard_Add(
            "식권이 발급되었습니다.",
            "주문번호: {}\n--------------------\n - 주문자: {}\n\n - 매장: {} \n - 메뉴: {}\n\n - 결제 금액: {}원\n\n - 픽업 시간: {}\n--------------------\n - 매장 위치: {}".format(
                pushedOrder.management_code,
                pushedOrder.userInstance.name,
                pushedOrder.storeInstance.name, 
                pushedOrder.menuInstance.name, 
                pushedOrder.menuInstance.price, 
                pushedOrder.pickupTime, 
                pushedOrder.storeInstance.addr
            ),
            thumbnail, buttons
        )

        for entryPoint in DEFAULT_QUICKREPLIES_MAP:
            KakaoForm.QuickReplies_Add(entryPoint['action'], entryPoint['label'], entryPoint['messageText'], entryPoint['blockid'], entryPoint['extra'])
        
        return JsonResponse(KakaoForm.GetForm())

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView("Get Pickup Time Error\n- {} ".format(ex))



