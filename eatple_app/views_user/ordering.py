'''
    Author : Ben Kim

    @NOTE
    @BUG
    @TODO
 
'''
# System
import sys
import os

# Django Library
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

# External Library
import requests
import json
from datetime import timedelta

# Models
from eatple_app.models import User
from eatple_app.models import Order, OrderManager
from eatple_app.models import Category, Tag
from eatple_app.models import Store, Menu

# Modules
from eatple_app.module_kakao.ReponseForm import Kakao_SimpleForm, Kakao_CarouselForm
from eatple_app.module_kakao.RequestForm import getLatLng, KakaoPayLoad

# View-System
from eatple_app.views_system.debugger import EatplusSkillLog, errorView

# Wordings
from eatple_app.views_user.wording import wordings

# Define
from eatple_app.define import EP_define, dateNowByTimeZone

HOST_URL = EP_define.HOST_URL

NOT_APPLICABLE = EP_define.NOT_APPLICABLE

SELLING_TIME_LUNCH = EP_define.SELLING_TIME_LUNCH
SELLING_TIME_DINNER = EP_define.SELLING_TIME_DINNER
SELLING_TIME_CATEGORY_DICT = EP_define.SELLING_TIME_CATEGORY_DICT
SELLING_TIME_CATEGORY = EP_define.SELLING_TIME_CATEGORY

LUNCH = SELLING_TIME_CATEGORY[SELLING_TIME_LUNCH][0]
DINNER = SELLING_TIME_CATEGORY[SELLING_TIME_DINNER][0]

LUNCH_PICKUP_TIME = EP_define.LUNCH_PICKUP_TIME
DINNER_PICKUP_TIME = EP_define.DINNER_PICKUP_TIME

ORDER_STATUS = EP_define.ORDER_STATUS
ORDER_STATUS_DICT = EP_define.ORDER_STATUS_DICT

KAKAO_PARAM_ORDER_ID = EP_define.KAKAO_PARAM_ORDER_ID
KAKAO_PARAM_STORE_ID = EP_define.KAKAO_PARAM_STORE_ID
KAKAO_PARAM_MENU_ID = EP_define.KAKAO_PARAM_MENU_ID

KAKAO_PARAM_MENU_CATEGORY = EP_define.KAKAO_PARAM_MENU_CATEGORY
KAKAO_PARAM_SELLING_TIME = EP_define.KAKAO_PARAM_SELLING_TIME
KAKAO_PARAM_PICKUP_TIME = EP_define.KAKAO_PARAM_PICKUP_TIME

KAKAO_PARAM_STATUS = EP_define.KAKAO_PARAM_STATUS
KAKAO_PARAM_STATUS_OK = EP_define.KAKAO_PARAM_STATUS_OK
KAKAO_PARAM_STATUS_NOT_OK = EP_define.KAKAO_PARAM_STATUS_NOT_OK

KAKAO_SUPER_USER_ID = EP_define.DEFAULT_USER_ID

# STATIC CONFIG
MENU_LIST_LENGTH = 5
CATEGORY_LIST_LENGTH = 5

DEFAULT_QUICKREPLIES_MAP = [
    {'action': "message", 'label': wordings.RETURN_HOME_QUICK_REPLISE,    'messageText': wordings.RETURN_HOME_QUICK_REPLISE, 'blockid': "none",
        'extra': {KAKAO_PARAM_STATUS: KAKAO_PARAM_STATUS_OK}},
]

# # # # # # # # # # # # # # # # # # # # # # # # #
#
# Static View
#
# # # # # # # # # # # # # # # # # # # # # # # # #


def orderValidation(userID, menuID):
    menuInstance = Menu.objects.get(id=menuID)

    # Double Order Check
    OrderManagerInstance = OrderManager(userID)
    if OrderManagerInstance.getAvailableLunchCouponPurchased().exists() and (menuInstance.sellingTime == SELLING_TIME_CATEGORY[SELLING_TIME_LUNCH][0]):
        return False

    elif OrderManagerInstance.getAvailableDinnerCouponPurchased().exists() and (menuInstance.sellingTime == SELLING_TIME_CATEGORY[SELLING_TIME_DINNER][0]):
        return False


'''
    @name sellingTimeCheck
    @param

    @note
    @bug
    @todo
'''


def sellingTimeCheck():
    nowDate = dateNowByTimeZone()
    nowDateWithoutTime = nowDate.replace(
        hour=0, minute=0, second=0, microsecond=0)

    # Prev Lunch Order Time 16:30 ~ 10:30
    prevlunchOrderTimeStart = nowDateWithoutTime + \
        timedelta(hours=16, minutes=30, days=-1)
    prevlunchOrderTimeEnd = nowDateWithoutTime + \
        timedelta(hours=10, minutes=30)

    # Dinner Order Time 10:30 ~ 16:30
    dinnerOrderTimeStart = nowDateWithoutTime + timedelta(hours=10, minutes=30)
    dinnerOrderTimeEnd = nowDateWithoutTime + timedelta(hours=16, minutes=30)

    # Next Lunch Order Time 16:30 ~ 10:30
    nextlunchOrderTimeStart = nowDateWithoutTime + \
        timedelta(hours=16, minutes=30)
    nextlunchOrderTimeEnd = nowDateWithoutTime + \
        timedelta(hours=10, minutes=30, days=1)

    if(dinnerOrderTimeStart <= nowDate) and (nowDate <= dinnerOrderTimeEnd):
        return SELLING_TIME_DINNER
    elif(prevlunchOrderTimeStart < nowDate) and (nowDate < prevlunchOrderTimeEnd):
        return SELLING_TIME_LUNCH
    elif(nextlunchOrderTimeStart < nowDate) and (nowDate < nextlunchOrderTimeEnd):
        return SELLING_TIME_LUNCH
    else:
        return None


'''
    @name MenuListup
    @param userID, menuCategory, sellingTime, currentSellingTime, location

    @note
    @bug
    @todo
'''


def MenuListup(userID, menuCategory, sellingTime, currentSellingTime, location):
    ALL_MENU = '전체'

    STORE_CATEGORY_QUICKREPLIES_MAP = [
        {'action': "message", 'label': wordings.HOME_QUICK_REPLISE, 'messageText': wordings.HOME_QUICK_REPLISE, 'blockid': "none",
         'extra': {KAKAO_PARAM_STATUS: KAKAO_PARAM_STATUS_OK}},
        {'action': "message", 'label': "전체",    'messageText': "{} {} 메뉴보기".format(sellingTime, ALL_MENU), 'blockid': "none",
         'extra': {KAKAO_PARAM_MENU_CATEGORY: NOT_APPLICABLE, KAKAO_PARAM_SELLING_TIME: sellingTime, }},
    ]

    ORDER_EXIT_QUICKREPLIES_MAP = [
        {'action': "message", 'label': wordings.RETURN_HOME_QUICK_REPLISE, 'messageText': wordings.RETURN_HOME_QUICK_REPLISE, 'blockid': "none",
         'extra': {KAKAO_PARAM_STATUS: KAKAO_PARAM_STATUS_OK}},
    ]

    # Check Selling Time
    if SELLING_TIME_CATEGORY[currentSellingTime][0] != sellingTime:
        KakaoForm = Kakao_SimpleForm()
        KakaoForm.SimpleForm_Init()

        if SELLING_TIME_CATEGORY[currentSellingTime][0] != LUNCH:
            KakaoForm.SimpleText_Add(
                wordings.GET_SELLING_TIME_LUNCH_FINISH_TEXT)
            ORDER_EXIT_QUICKREPLIES_MAP.append({'action': "message", 'label': wordings.GET_SELLING_TIME_DINNER_BTN,    'messageText': wordings.GET_SELLING_TIME_DINNER_BTN, 'blockid': "none",
                                                'extra': {KAKAO_PARAM_MENU_CATEGORY: NOT_APPLICABLE,
                                                          KAKAO_PARAM_SELLING_TIME: DINNER, }})
        else:
            KakaoForm.SimpleText_Add(
                wordings.GET_SELLING_TIME_DINNER_FINISH_TEXT)
            ORDER_EXIT_QUICKREPLIES_MAP.append({'action': "message", 'label': wordings.GET_SELLING_TIME_LUNCH_BTN,    'messageText': wordings.GET_SELLING_TIME_LUNCH_BTN, 'blockid': "none",
                                                'extra': {KAKAO_PARAM_MENU_CATEGORY: NOT_APPLICABLE,
                                                          KAKAO_PARAM_SELLING_TIME: DINNER, }})

        for entryPoint in ORDER_EXIT_QUICKREPLIES_MAP:
            KakaoForm.QuickReplies_Add(entryPoint['action'], entryPoint['label'],
                                       entryPoint['messageText'], entryPoint['blockid'], entryPoint['extra'])

        return JsonResponse(KakaoForm.GetForm())

    # Check User Order
    OrderManagerInstance = OrderManager(userID)

    if OrderManagerInstance.availableCouponStatusUpdate().exists():
        KakaoForm = Kakao_SimpleForm()
        KakaoForm.SimpleForm_Init()

        for entryPoint in DEFAULT_QUICKREPLIES_MAP:
            KakaoForm.QuickReplies_Add(entryPoint['action'], entryPoint['label'],
                                       entryPoint['messageText'], entryPoint['blockid'], entryPoint['extra'])

        if OrderManagerInstance.getAvailableLunchCouponPurchased().exists() and (sellingTime == SELLING_TIME_CATEGORY[SELLING_TIME_LUNCH][0]):
            KakaoForm.SimpleText_Add(wordings.ALREADY_ORDER_LUNCH_TEXT)
            return JsonResponse(KakaoForm.GetForm())

        elif OrderManagerInstance.getAvailableDinnerCouponPurchased().exists() and (sellingTime == SELLING_TIME_CATEGORY[SELLING_TIME_DINNER][0]):
            KakaoForm.SimpleText_Add(wordings.ALREADY_ORDER_DINNER_TEXT)
            return JsonResponse(KakaoForm.GetForm())

    CategoryList = Category.objects.all()[:CATEGORY_LIST_LENGTH]
    for category in CategoryList:
        STORE_CATEGORY_QUICKREPLIES_MAP.append({'action': "message", 'label': category.name, 'messageText': "{} {} {}".format(sellingTime, category.name, wordings.GET_MENU_COMMAND), 'blockid': "none",
                                                'extra': {KAKAO_PARAM_MENU_CATEGORY: category.name, KAKAO_PARAM_SELLING_TIME: sellingTime}})

    if(menuCategory == NOT_APPLICABLE) or (menuCategory == ALL_MENU):
        MenuList = Menu.objects.filter(sellingTime=sellingTime)[
            :MENU_LIST_LENGTH]
    else:
        MenuList = Menu.objects.filter(
            categories__category__name=menuCategory, sellingTime=sellingTime)[:MENU_LIST_LENGTH]

    if MenuList:
        KakaoForm = Kakao_CarouselForm()
        KakaoForm.BasicCard_Init()

        # Menu Carousel Card Add
        for menu in MenuList:
            try:
                thumbnail = {"imageUrl": "{}{}".format(
                    HOST_URL, menu.imgURL())}
                kakaoMapUrl = "https://map.kakao.com/link/map/{},{}".format(
                    menu.storeInstance.name, getLatLng(menu.storeInstance.addr))
            except () as ex:
                print(ex)

            buttons = [
                {'action': "message", 'label': wordings.ORDER_BTN,  'messageText': "{} {}".format(sellingTime, wordings.GET_PICKUP_TIME_COMMAND),
                 'extra': {
                    KAKAO_PARAM_STORE_ID:         menu.storeInstance.id,
                    KAKAO_PARAM_MENU_ID:          menu.id,
                    KAKAO_PARAM_MENU_CATEGORY:    menuCategory,
                    KAKAO_PARAM_SELLING_TIME:     sellingTime,
                }},

                {'action': "webLink", 'label': wordings.SHOW_LOCATION_BTN,
                    "webLinkUrl": kakaoMapUrl},
            ]

            KakaoForm.BasicCard_Add("{}".format(menu.name), "{} - {}원".format(
                menu.storeInstance.name,
                menu.price
            ), thumbnail, buttons)

        # Quick Replise Add
        for entryPoint in STORE_CATEGORY_QUICKREPLIES_MAP:
            KakaoForm.QuickReplies_Add(entryPoint['action'], entryPoint['label'],
                                       entryPoint['messageText'], entryPoint['blockid'], entryPoint['extra'])

    else:
        KakaoForm = Kakao_SimpleForm()
        KakaoForm.SimpleForm_Init()

        if menuCategory == NOT_APPLICABLE:
            for entryPoint in ORDER_EXIT_QUICKREPLIES_MAP:
                KakaoForm.QuickReplies_Add(
                    entryPoint['action'], entryPoint['label'], entryPoint['messageText'], entryPoint['blockid'], entryPoint['extra'])

            KakaoForm.SimpleText_Add("판매중인 {} 메뉴가 없어요ㅠㅜ".format(sellingTime))
        else:
            KakaoForm = Kakao_SimpleForm()
            KakaoForm.SimpleForm_Init()

            for entryPoint in STORE_CATEGORY_QUICKREPLIES_MAP:
                KakaoForm.QuickReplies_Add(
                    entryPoint['action'], entryPoint['label'], entryPoint['messageText'], entryPoint['blockid'], entryPoint['extra'])

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
'''
    @name GET_SellingTime
    @param userID

    @note
    @bug
    @todo
'''
@csrf_exempt
def GET_SellingTime(request):
    try:
        kakaoPayload = KakaoPayLoad(request)

        # Invalied Path Access
        if(kakaoPayload.userID == NOT_APPLICABLE):
            return errorView("Parameter Error")
        else:
            try:
                userInstance = User.objects.get(
                    identifier_code=kakaoPayload.userID)
            except User.DoesNotExist:
                return errorView("User ID is Invalid")

        EatplusSkillLog("Order Flow")

        OrderManagerInstance = OrderManager(kakaoPayload.userID)
        if OrderManagerInstance.getAvailableLunchCouponPurchased().exists() and OrderManagerInstance.getAvailableDinnerCouponPurchased().exists():
            KakaoForm = Kakao_SimpleForm()
            KakaoForm.SimpleForm_Init()

            KakaoForm.SimpleText_Add(wordings.ALREADY_ORDER_EATPLUS_TEXT)

            for entryPoint in DEFAULT_QUICKREPLIES_MAP:
                KakaoForm.QuickReplies_Add(
                    entryPoint['action'], entryPoint['label'], entryPoint['messageText'], entryPoint['blockid'], entryPoint['extra'])

            return JsonResponse(KakaoForm.GetForm())
        else:
            KakaoForm = Kakao_CarouselForm()
            KakaoForm.BasicCard_Init()

            thumbnail = {"imageUrl": ""}

            buttons = [
                {'action': "message", 'label': wordings.GET_SELLING_TIME_LUNCH_BTN,  'messageText': wordings.GET_SELLING_TIME_LUNCH_BTN,
                 'extra': {KAKAO_PARAM_MENU_CATEGORY: NOT_APPLICABLE,
                           KAKAO_PARAM_SELLING_TIME: LUNCH, }
                 },

                {'action': "message", 'label': wordings.GET_SELLING_TIME_DINNER_BTN,  'messageText': wordings.GET_SELLING_TIME_DINNER_BTN,
                 'extra': {KAKAO_PARAM_MENU_CATEGORY: NOT_APPLICABLE,
                           KAKAO_PARAM_SELLING_TIME: DINNER, }
                 }
            ]

            KakaoForm.BasicCard_Add(wordings.GET_SELLING_TIME_SELECT_TITLE_TEXT,
                                    wordings.GET_SELLING_TIME_SELECT_DESCRIPT_TEXT, thumbnail, buttons)

            for entryPoint in DEFAULT_QUICKREPLIES_MAP:
                KakaoForm.QuickReplies_Add(
                    entryPoint['action'], entryPoint['label'], entryPoint['messageText'], entryPoint['blockid'], entryPoint['extra'])

            return JsonResponse(KakaoForm.GetForm())

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView("{}".format(ex))


'''
    @name GET_Menu
    @param userID, sellingTime 

    @note
    @bug
    @todo
'''
@csrf_exempt
def GET_Menu(request):
    try:
        kakaoPayload = KakaoPayLoad(request)

        # Invalied Path Access
        # and (kakaoPayload.menuCategory == NOT_APPLICABLE) => "ALL MENU"
        if(kakaoPayload.userID == NOT_APPLICABLE) or (kakaoPayload.sellingTime == NOT_APPLICABLE):
            return errorView("Parameter Error")
        else:
            try:
                userInstance = User.objects.get(
                    identifier_code=kakaoPayload.userID)
            except User.DoesNotExist:
                return errorView("User ID is Invalid")

        EatplusSkillLog("Order Flow")

        # Selling Time Check
        currentSellingTime = sellingTimeCheck()
        if currentSellingTime == None:
            return errorView("Get Invalid Selling Time")

        return MenuListup(userInstance.identifier_code, kakaoPayload.menuCategory, kakaoPayload.sellingTime, currentSellingTime, kakaoPayload.location)

    except (RuntimeError, TypeError, NameError, KeyError, AttributeError, ValueError) as ex:
        return errorView("{}".format(ex))


'''
    @name GET_PickupTime
    @param userID, storeID, menuID, sellingTime 

    @note
    @bug
    @todo
'''
@csrf_exempt
def GET_PickupTime(request):
    try:
        kakaoPayload = KakaoPayLoad(request)

        # Invalied Path Access
        if(kakaoPayload.userID == NOT_APPLICABLE) or (kakaoPayload.storeID == NOT_APPLICABLE) or (kakaoPayload.menuID == NOT_APPLICABLE) or (kakaoPayload.sellingTime == NOT_APPLICABLE):
            return errorView("Parameter Error")
        else:
            try:
                userInstance = User.objects.get(
                    identifier_code=kakaoPayload.userID)
            except User.DoesNotExist:
                return errorView("User ID is Invalid")

            storeInstance = Store.objects.get(id=kakaoPayload.storeID)
            menuInstance = Menu.objects.get(id=kakaoPayload.menuID)

        if(orderValidation(kakaoPayload.userID, kakaoPayload.menuID) == False):
            return errorView("Order Validate Failed!", "정상적인 경로로 주문해주세요!")

        EatplusSkillLog("Order Flow")

        KakaoForm = Kakao_SimpleForm()
        KakaoForm.SimpleForm_Init()

        KakaoForm.SimpleText_Add(
            "{} 픽업시간을 설정해주세요.".format(kakaoPayload.sellingTime))

        allExtraData = kakaoPayload.dataActionExtra

        PICKUP_TIME_QUICKREPLIES_MAP = []

        if SELLING_TIME_CATEGORY_DICT[kakaoPayload.sellingTime] == SELLING_TIME_LUNCH:
            ENTRY_PICKUP_TIME_MAP = LUNCH_PICKUP_TIME
            pikcupTime_Start = storeInstance.lunch_pickupTime_start
            pikcupTime_End = storeInstance.lunch_pickupTime_end
        else:
            ENTRY_PICKUP_TIME_MAP = DINNER_PICKUP_TIME
            pikcupTime_Start = storeInstance.dinner_pickupTime_start
            pikcupTime_End = storeInstance.dinner_pickupTime_end

        for index, pickupTime in ENTRY_PICKUP_TIME_MAP:
            if(pikcupTime_Start <= index) and (index <= pikcupTime_End):
                PICKUP_TIME_QUICKREPLIES_MAP += {'action': "message", 'label': pickupTime, 'messageText': wordings.ORDER_CONFIRM_COMMAND,
                                                 'blockid': "none", 'extra': {**allExtraData, KAKAO_PARAM_PICKUP_TIME: pickupTime}},

        for entryPoint in PICKUP_TIME_QUICKREPLIES_MAP:
            KakaoForm.QuickReplies_Add(entryPoint['action'], entryPoint['label'],
                                       entryPoint['messageText'], entryPoint['blockid'], entryPoint['extra'])

        return JsonResponse(KakaoForm.GetForm())

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView("{}".format(ex))


'''
    @name SET_OrderSheet
    @param storeID, menuID, userID, pickupTime

    @note
    @bug
    @todo
'''
@csrf_exempt
def SET_OrderSheet(request):
    try:
        kakaoPayload = KakaoPayLoad(request)

        # Invalied Path Access
        if(kakaoPayload.userID == NOT_APPLICABLE) or (kakaoPayload.storeID == NOT_APPLICABLE) or (kakaoPayload.menuID == NOT_APPLICABLE) or (kakaoPayload.pickupTime == NOT_APPLICABLE):
            return errorView("Parameter Error")
        else:
            try:
                userInstance = User.objects.get(
                    identifier_code=kakaoPayload.userID)
            except User.DoesNotExist:
                return errorView("User ID is Invalid")

            storeInstance = Store.objects.get(id=kakaoPayload.storeID)
            menuInstance = Menu.objects.get(id=kakaoPayload.menuID)

        if(orderValidation(kakaoPayload.userID, kakaoPayload.menuID) == False):
            return errorView("Order Validate Failed!", "정상적인 경로로 주문해주세요!")

        EatplusSkillLog("Order Flow")

        KakaoForm = Kakao_CarouselForm()
        KakaoForm.BasicCard_Init()

        # Menu Carousel Card Add
        thumbnail = {"imageUrl": "{}{}".format(
            HOST_URL, menuInstance.imgURL())}

        kakaoMapUrl = "https://map.kakao.com/link/map/{},{}".format(
            storeInstance.name, getLatLng(storeInstance.addr))
        buttons = [
            # {'action': "webLink", 'label': wordings.ORDER_PUSH_COMMAND,  'messageText': wordings.ORDER_PUSH_COMMAND, 'extra': kakaoPayload.dataActionExtra,

            # "webLinkUrl": "http://eatple.com/payment?storeName={storeName}&menuName={menuName}&menuPrice={menuPrice}".format(storeName=storeInstance.name, menuName=menuInstance.name, menuPrice=menuInstance.price )},
            # "webLinkUrl": "http://localhost:3000/payment?storeName={storeName}&menuName={menuName}&menuPrice={menuPrice}".format(storeName=storeInstance.name, menuName=menuInstance.name, menuPrice=menuInstance.price )},

            {'action': "message", 'label': wordings.ORDER_PUSH_COMMAND,
                'messageText': wordings.ORDER_PUSH_COMMAND, 'extra': kakaoPayload.dataActionExtra}
        ]

        KakaoForm.BasicCard_Add("{}".format(menuInstance.name), "{} - {}원\n - 픽업 시간 [ {} ]".format(
            storeInstance.name,
            menuInstance.price,
            kakaoPayload.pickupTime
        ), thumbnail, buttons)

        GET_PICKUP_TIME_QUICKREPLIES_MAP = [
            {'action': "message", 'label': "{}하기".format(wordings.ORDER_PICKUP_TIME_CHANGE_COMMAND),  'messageText': "{} {}".format(
                kakaoPayload.sellingTime, wordings.GET_PICKUP_TIME_COMMAND), 'blockid': "none", 'extra': kakaoPayload.dataActionExtra},
            {'action': "message", 'label': wordings.RETURN_HOME_QUICK_REPLISE, 'messageText': wordings.RETURN_HOME_QUICK_REPLISE,
                'blockid': "none", 'extra': {KAKAO_PARAM_STATUS: KAKAO_PARAM_STATUS_OK}},
        ]

        for entryPoint in GET_PICKUP_TIME_QUICKREPLIES_MAP:
            KakaoForm.QuickReplies_Add(entryPoint['action'], entryPoint['label'],
                                       entryPoint['messageText'], entryPoint['blockid'], entryPoint['extra'])

        return JsonResponse(KakaoForm.GetForm())

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView("{}".format(ex))


'''
    @name POST_Order
    @param storeID, menuID, userID, pickupTime

    @note
    @bug
    @todo
'''
@csrf_exempt
def POST_Order(request):
    try:
        kakaoPayload = KakaoPayLoad(request)

        # Invalied Path Access
        if(kakaoPayload.userID == NOT_APPLICABLE) or (kakaoPayload.storeID == NOT_APPLICABLE) or (kakaoPayload.menuID == NOT_APPLICABLE) or (kakaoPayload.pickupTime == NOT_APPLICABLE):
            return errorView("Parameter Invalid")
        else:
            try:
                userInstance = User.objects.get(
                    identifier_code=kakaoPayload.userID)
            except User.DoesNotExist:
                return errorView("User ID is Invalid")

            storeInstance = Store.objects.get(id=kakaoPayload.storeID)
            menuInstance = Menu.objects.get(id=kakaoPayload.menuID)

        if(orderValidation(kakaoPayload.userID, kakaoPayload.menuID) == False):
            return errorView("Order Validate Failed!", "정상적인 경로로 주문해주세요!")

        # Order Validation
        OrderManagerInstance = OrderManager(kakaoPayload.userID)
        if OrderManagerInstance.getAvailableLunchCouponPurchased().exists() and (menuInstance.sellingTime == SELLING_TIME_CATEGORY[SELLING_TIME_LUNCH][0]):
            return errorView("Invalid Access Order")

        elif OrderManagerInstance.getAvailableDinnerCouponPurchased().exists() and (menuInstance.sellingTime == SELLING_TIME_CATEGORY[SELLING_TIME_DINNER][0]):
            return errorView("Invalid Access Order")

        EatplusSkillLog("Order Flow")

        requests.get

        pushedOrder = Order.pushOrder(userInstance=userInstance,
                                      storeInstance=storeInstance,
                                      menuInstance=menuInstance,
                                      pickupTime=kakaoPayload.pickupTime)

        KakaoForm = Kakao_CarouselForm()
        KakaoForm.BasicCard_Init()

        thumbnail = {"imageUrl": ""}

        kakaoMapUrl = "https://map.kakao.com/link/map/{},{}".format(
            storeInstance.name, getLatLng(storeInstance.addr))

        buttons = [
            {'action': "webLink", 'label': wordings.SHOW_LOCATION_BTN,
                "webLinkUrl": kakaoMapUrl},
            {'action': "message", 'label': wordings.ORDER_CANCEL_COMMAND,  'messageText': wordings.ORDER_CANCEL_COMMAND,
             'extra': {KAKAO_PARAM_ORDER_ID: pushedOrder.id}}
        ]

        KakaoForm.BasicCard_Add(
            "잇플패스가 발급되었습니다.",
            "주문번호: {}\n--------------------\n - 주문자: {}\n\n - 매장: {} \n - 메뉴: {}\n\n - 제 금액: {}원\n\n - 픽업 시간: {}\n--------------------\n - 매장 위치: {}".format(
                pushedOrder.management_code,
                pushedOrder.userInstance.name,
                pushedOrder.storeInstance.name,
                pushedOrder.menuInstance.name,
                pushedOrder.menuInstance.price,
                pushedOrder.pickupTime.astimezone().strftime('%H시%M분 %m월%d일'),
                pushedOrder.storeInstance.addr
            ),
            thumbnail, buttons
        )

        for entryPoint in DEFAULT_QUICKREPLIES_MAP:
            KakaoForm.QuickReplies_Add(entryPoint['action'], entryPoint['label'],
                                       entryPoint['messageText'], entryPoint['blockid'], entryPoint['extra'])

        return JsonResponse(KakaoForm.GetForm())

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView("{}".format(ex))
