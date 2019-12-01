# Django Library
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

# Models
from eatple_app.models import *

# Define
from eatple_app.define import *

# Modules
from eatple_app.module_kakao.ReponseForm import *
from eatple_app.module_kakao.RequestForm import *
from eatple_app.module_kakao.Validation import *

# View-System
from eatple_app.views_system.debugger import *

from eatple_app.views import *


# STATIC CONFIG
MENU_LIST_LENGTH = 10

DISCOUNT_FOR_DEBUG = 5900

# # # # # # # # # # # # # # # # # # # # # # # # #
#
# Static View
#
# # # # # # # # # # # # # # # # # # # # # # # # #

def sellingTimeCheck():
    nowDate = dateNowByTimeZone()
    nowDateWithoutTime = nowDate.replace(
        hour=0, minute=0, second=0, microsecond=0)

    # Prev Lunch Order Time 16:30 ~ 10:30
    prevlunchOrderTimeStart = nowDateWithoutTime + \
        datetime.timedelta(hours=16, minutes=30, days=-1)
    prevlunchOrderTimeEnd = nowDateWithoutTime + \
        datetime.timedelta(hours=10, minutes=30)

    # Dinner Order Time 10:30 ~ 16:30
    dinnerOrderTimeStart = nowDateWithoutTime + datetime.timedelta(hours=10, minutes=30)
    dinnerOrderTimeEnd = nowDateWithoutTime + datetime.timedelta(hours=16, minutes=30)

    # Next Lunch Order Time 16:30 ~ 10:30
    nextlunchOrderTimeStart = nowDateWithoutTime + \
        datetime.timedelta(hours=16, minutes=30)
    nextlunchOrderTimeEnd = nowDateWithoutTime + \
        datetime.timedelta(hours=10, minutes=30, days=1)

    if(dinnerOrderTimeStart <= nowDate) and (nowDate <= dinnerOrderTimeEnd):
        return SELLING_TIME_DINNER
    elif(prevlunchOrderTimeStart < nowDate) and (nowDate < prevlunchOrderTimeEnd):
        return SELLING_TIME_LUNCH
    elif(nextlunchOrderTimeStart < nowDate) and (nowDate < nextlunchOrderTimeEnd):
        return SELLING_TIME_LUNCH
    else:
        return None

def kakaoView_MenuListup(kakaoPayload):
    # Block Validation
    prev_block_id = prevBlockValidation(kakaoPayload)
    if(prev_block_id != KAKAO_BLOCK_HOME and 
       prev_block_id != KAKAO_BLOCK_EATPLE_PASS and
       prev_block_id != KAKAO_BLOCK_ORDER_DETAILS):
        return errorView("Invalid Block Access", "정상적이지 않은 경로거나, 오류가 발생했습니다.\n다시 주문해주세요!")

    # User Validation
    user = userValidation(kakaoPayload)
    if (user == None):
        return GET_UserHome(request)

    # User's Eatple Pass Validation
    eatplePassStatus = eatplePassValidation(user)
    if(eatplePassStatus != None):
        return eatplePassStatus
    
    sellingTime = sellingTimeCheck()

    # Order Log Record
    orderRecordSheet = OrderRecordSheet()
    orderRecordSheet.user = user
    orderRecordSheet.recordUpdate(ORDER_RECORD_GET_MENU)

    if (sellingTime == None):
        return errorView("Get Invalid Selling Time", "잘못된 주문 시간입니다.")
    elif sellingTime == SELLING_TIME_DINNER:
        """
            @NOTE Dinner Time Close In Alpha 
        """

        # return kakaoView_MenuListup(user, SELLING_TIME_LUNCH)
        return errorView("Get Invalid Selling Time", "오늘 점심은 이미 마감되었어요.\n내일 점심을 기대해주세요.")


    menuList = Menu.objects.filter(sellingTime=sellingTime)[:MENU_LIST_LENGTH]

    if menuList:
        KakaoForm = Kakao_CarouselForm()
        KakaoForm.BasicCard_Init()

        # Menu Carousel Card Add
        for menu in menuList:
            thumbnail = {"imageUrl": "{}{}".format(
                HOST_URL, menu.imgURL())}

            kakaoMapUrl = "https://map.kakao.com/link/map/{},{}".format(
                menu.store.name, getLatLng(menu.store.addr))

            buttons = [
                {
                    'action': "block",
                    'label': "주문하기",
                    'messageText': "로딩중..",
                    'blockId': KAKAO_BLOCK_SET_PICKUP_TIME,
                    'extra': {
                        KAKAO_PARAM_STORE_ID: menu.store.store_id,
                        KAKAO_PARAM_MENU_ID: menu.menu_id,
                        KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_GET_MENU
                    }
                },
                {
                    'action': "webLink",
                    'label': "위치보기",
                    "webLinkUrl": kakaoMapUrl
                },
            ]

            KakaoForm.BasicCard_Add(
                "{}".format(menu.name), 
                "{} - {}원".format(
                    menu.store.name,
                    menu.price
                ), 
                thumbnail, 
                buttons
            )

    else:
        KakaoForm = Kakao_SimpleForm()
        KakaoForm.SimpleForm_Init()

        KakaoForm.SimpleText_Add("판매중인 메뉴가 없어요...")

    QUICKREPLIES_MAP = [
        {
            'action': "block",
            'label': "홈으로 돌아가기",
            'messageText': "로딩중..",
            'blockId': KAKAO_BLOCK_HOME,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_GET_MENU
            }
        },
    ]

    KakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)
        

    return JsonResponse(KakaoForm.GetForm())

def kakaoView_PickupTime(kakaoPayload):
    # Block Validation
    prev_block_id = prevBlockValidation(kakaoPayload)
    if(prev_block_id != KAKAO_BLOCK_GET_MENU and prev_block_id != KAKAO_BLOCK_SET_ORDER_SHEET):
        return errorView("Invalid Block Access", "정상적이지 않은 경로거나, 오류가 발생했습니다.\n다시 주문해주세요!")

    # User Validation
    user = userValidation(kakaoPayload)
    if (user == None):
        return GET_UserHome(request)


    order = orderValidation(kakaoPayload)
    if(order != None):
        orderManager = OrderManager(user)
        orderManager.orderPaidCheck()
        
        order = orderValidation(kakaoPayload)
        print(order)
        
        if(order.payment_status == IAMPORT_ORDER_STATUS_PAID):
            return errorView("Invalid Block Access", "이미 주문이 완료되었습니다!\n픽업시간 변경을 원하시면 잇플패스 내역에서\n 픽업시간을 변경해주세요.")
    
    
    # User's Eatple Pass Validation
    eatplePassStatus = eatplePassValidation(user)
    if(eatplePassStatus != None):
        return eatplePassStatus

    store = storeValidation(kakaoPayload)
    menu = menuValidation(kakaoPayload)
    
    if(store == None or menu == None):
        return errorView("Invalid Store Paratmer", "정상적이지 않은 경로거나, 오류가 발생했습니다.\n다시 주문해주세요!")

    currentSellingTime = sellingTimeCheck()

    # Order Record
    try:
        orderRecordSheet = OrderRecordSheet.objects.latest('update_date')
    except OrderRecordSheet.DoesNotExist:
        orderRecordSheet = OrderRecordSheet()

    if (orderRecordSheet.timeoutValidation()):
        return kakaoView_TimeOut(KAKAO_BLOCK_SET_PICKUP_TIME)

    orderRecordSheet.user = user
    orderRecordSheet.menu = menu
    orderRecordSheet.recordUpdate(ORDER_RECORD_SET_PICKUP_TIEM)

    KakaoForm = Kakao_SimpleForm()
    KakaoForm.SimpleForm_Init()

    KakaoForm.SimpleText_Add(
        "음식을 가지러 갈 픽업시간을 설정해주세요."
    )

    PICKUP_TIME_QUICKREPLIES_MAP = []

    pickupTimes = PickupTime.objects.filter(store=store)

    order = orderValidation(kakaoPayload)
        
    for pickupTime in pickupTimes:
        dataActionExtra = {
            KAKAO_PARAM_STORE_ID: menu.store.store_id,
            KAKAO_PARAM_MENU_ID: menu.menu_id,
            KAKAO_PARAM_PICKUP_TIME: pickupTime.time.strftime('%H:%M'),
            KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_SET_PICKUP_TIME
        }
        
        if(order != None):
            dataActionExtra[KAKAO_PARAM_ORDER_ID] = order.order_id
        
        KakaoForm.QuickReplies_Add(
            'block',
            pickupTime.time.strftime('%H:%M'),
            '로딩중..',
            KAKAO_BLOCK_SET_ORDER_SHEET,
            dataActionExtra
        )

    return JsonResponse(KakaoForm.GetForm())

def kakaoView_OrderPayment(kakaoPayload):
    # Block Validation
    prev_block_id = prevBlockValidation(kakaoPayload)
    if(prev_block_id != KAKAO_BLOCK_SET_PICKUP_TIME and prev_block_id != KAKAO_BLOCK_SET_ORDER_SHEET):
        return errorView("Invalid Block Access", "정상적이지 않은 경로거나, 오류가 발생했습니다.\n다시 주문해주세요!")

    # User Validation
    user = userValidation(kakaoPayload)
    if (user == None):
        return GET_UserHome(request)

    # User's Eatple Pass Validation
    eatplePassStatus = eatplePassValidation(user)
    if(eatplePassStatus != None):
        return eatplePassStatus

    store = storeValidation(kakaoPayload)
    menu = menuValidation(kakaoPayload)
    pickup_time = pickupTimeValidation(kakaoPayload)
    
    if(store == None or menu == None or pickup_time == None ):
        return errorView("Invalid Store Paratmer", "정상적이지 않은 경로거나, 오류가 발생했습니다.\n다시 주문해주세요!")

    discount = DISCOUNT_FOR_DEBUG
    if(discount != None):
        discountPrice = menu.price - discount
    else:
        discountPrice = menu.price

    order = orderValidation(kakaoPayload)
    if(order == None):
        orderSheet = OrderSheet()
        order = orderSheet.pushOrder(
            user=user,
            menu=menu,
            store=store,
            pickup_time=pickup_time,
            totalPrice=discountPrice,
            count=1,
        )
    else:
        order.pickup_time = order.pickupTimeToDateTime(pickup_time)
        order.totalPrice = discountPrice
        order.save()

    # Order Record
    try:
        orderRecordSheet = OrderRecordSheet.objects.latest('update_date')
    except OrderRecordSheet.DoesNotExist:
        orderRecordSheet = OrderRecordSheet()

    if (orderRecordSheet.timeoutValidation()):
        return kakaoView_TimeOut(KAKAO_BLOCK_SET_ORDER_SHEET)

    orderRecordSheet.user = user
    orderRecordSheet.menu = menu
    orderRecordSheet.recordUpdate(ORDER_RECORD_ORDERSHEET_CHECK)
    
    dataActionExtra = kakaoPayload.dataActionExtra
    dataActionExtra[KAKAO_PARAM_ORDER_ID] = order.order_id
    dataActionExtra[KAKAO_PARAM_PREV_BLOCK_ID] = KAKAO_BLOCK_SET_ORDER_SHEET

    KakaoForm = Kakao_CarouselForm()
    KakaoForm.ComerceCard_Init()

    # Menu Carousel Card Add
    thumbnails = [
        {
            "imageUrl": "{}{}".format(HOST_URL, menu.imgURL())}
    ]

    profile = {
        "nickname": "{name} - [ 픽업 : {pickup_time} ]".format(name=menu.name, pickup_time=pickup_time),
        "imageUrl": None
    }

    kakaoMapUrl = "https://map.kakao.com/link/map/{},{}".format(
        store.name, getLatLng(store.addr))
    
    buttons = [
        {
            'action': "webLink",
            'label': "결제하러 가기",
            'messageText': "로딩중..",
            'extra': dataActionExtra,

            "webLinkUrl": "http://eatple.com/payment?merchant_uid={merchant_uid}&storeName={storeName}&menuName={menuName}&menuPrice={menuPrice}&buyer_name={buyer_name}&buyer_tel={buyer_tel}&buyer_email={buyer_email}".format(
                merchant_uid=order.order_id,
                storeName=store.name,
                menuName=menu.name,
                menuPrice=order.totalPrice,
                buyer_name=user.app_user_id,
                buyer_tel=str(user.phone_number)[3:13],
                buyer_email=user.email,
            )
        },
        {
            'action': "block",
            'label': "식권 발급",
            'messageText': "로딩중..",
            'blockId': KAKAO_BLOCK_SET_ORDER_SHEET,
            'extra': dataActionExtra,
        },
    ]

    KakaoForm.ComerceCard_Add(
        "결제를 완료한 후에 \n식권 발급 버튼을 눌러주세요!".format(pickup_time=pickup_time),
        menu.price,
        discount,
        thumbnails,
        profile,
        buttons
    )

    GET_PICKUP_TIME_QUICKREPLIES_MAP = [
        {
            'action': "block", 'label': "픽업시간 변경하기",
            'messageText': "로딩중..",
            'blockId': KAKAO_BLOCK_SET_PICKUP_TIME,
            'extra': dataActionExtra
        },
        {
            'action': "message", 'label': "홈으로 돌아가기",
            'messageText': "로딩중..",
            'blockId': KAKAO_BLOCK_HOME,
            'extra': {}
        },
    ]
        
    KakaoForm.QuickReplies_AddWithMap(GET_PICKUP_TIME_QUICKREPLIES_MAP)

    return JsonResponse(KakaoForm.GetForm())

def kakaoView_OrderPaymentCheck(kakaoPayload):
    # Block Validation
    prev_block_id = prevBlockValidation(kakaoPayload)
    if(prev_block_id != KAKAO_BLOCK_SET_ORDER_SHEET):
        return errorView("Invalid Block Access", "정상적이지 않은 경로거나, 오류가 발생했습니다.\n다시 주문해주세요!")
    
    # User Validation
    user = userValidation(kakaoPayload)
    if (user == None):
        return GET_UserHome(request)

    store = storeValidation(kakaoPayload)
    menu = menuValidation(kakaoPayload)
    order = orderValidation(kakaoPayload)
    
    if(store == None or menu == None or order == None ):
        return errorView("Invalid Store Paratmer", "정상적이지 않은 경로거나, 오류가 발생했습니다.\n다시 주문해주세요!")

    # Order Record
    try:
        orderRecordSheet = OrderRecordSheet.objects.latest('update_date')
    except OrderRecordSheet.DoesNotExist:
        orderRecordSheet = OrderRecordSheet()
        
    if (orderRecordSheet.timeoutValidation()):
        return kakaoView_TimeOut(KAKAO_BLOCK_SET_ORDER_SHEET)

    orderRecordSheet.user = user
    orderRecordSheet.menu = menu
    orderRecordSheet.recordUpdate(ORDER_RECORD_PAYMENT)
    
    dataActionExtra = kakaoPayload.dataActionExtra
    dataActionExtra[KAKAO_PARAM_ORDER_ID] = order.order_id
    dataActionExtra[KAKAO_PARAM_PREV_BLOCK_ID] = KAKAO_BLOCK_SET_ORDER_SHEET

    iamport = Iamport(imp_key=IAMPORT_API_KEY, imp_secret=IAMPORT_API_SECRET_KEY)
    
    try:
        response = iamport.find(merchant_uid=order.order_id)
    except (KeyError, Iamport.ResponseError):
         return errorView("Invalid Store Paratmer", "정상적이지 않은 경로거나, 오류가 발생했습니다.\n다시 주문해주세요!")
    except Iamport.HttpError as http_error:
        response = {}
        response['status']=IAMPORT_ORDER_STATUS_READY

    if(response['status'] == IAMPORT_ORDER_STATUS_PAID):        
        return kakaoView_EatplePassIssuance(kakaoPayload)
    else:
        KakaoForm = Kakao_CarouselForm()
        KakaoForm.BasicCard_Init()

        BTN_MAP = [
            {
                'action': "webLink",
                'label': "결제하러 가기",
                'messageText': "로딩중..",
                'extra': dataActionExtra,

                "webLinkUrl": "http://eatple.com/payment?merchant_uid={merchant_uid}&storeName={storeName}&menuName={menuName}&menuPrice={menuPrice}&buyer_name={buyer_name}&buyer_tel={buyer_tel}&buyer_email={buyer_email}".format(
                    merchant_uid=order.order_id,
                    storeName=store.name,
                    menuName=menu.name,
                    menuPrice=order.totalPrice,
                    buyer_name=user.app_user_id,
                    buyer_tel=str(user.phone_number)[3:13],
                    buyer_email=user.email,
                )
            },
            {
                'action': "block",
                'label': "식권 발급",
                'messageText': "로딩중..",
                'blockId': KAKAO_BLOCK_SET_ORDER_SHEET,
                'extra': dataActionExtra,
            },
        ]
        
        QUICKREPLIES_MAP = [
            {
                'action': "block", 'label': "픽업시간 변경하기",
                'messageText': "로딩중..",
                'blockId': KAKAO_BLOCK_SET_PICKUP_TIME,
                'extra': dataActionExtra
            },
            {
                'action': "message", 'label': "홈으로 돌아가기",
                'messageText': "로딩중..",
                'blockId': KAKAO_BLOCK_HOME,
                'extra': {}
            },
        ]

        thumbnail = {"imageUrl": ""}

        buttons = BTN_MAP

        KakaoForm.BasicCard_Add(
            "아직 결제가 완료되지 않았어요!",
            "{menu} - {price}원".format(menu=menu.name, price=order.totalPrice),
            thumbnail, 
            buttons
        )

        KakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)

        return JsonResponse(KakaoForm.GetForm())

def kakaoView_EatplePassIssuance(kakaoPayload):
    try:
        # Block Validation
        prev_block_id = prevBlockValidation(kakaoPayload)
        if(prev_block_id != KAKAO_BLOCK_SET_ORDER_SHEET):
            return errorView("Invalid Block Access", "정상적이지 않은 경로거나, 오류가 발생했습니다.")
        
        # User Validation
        user = userValidation(kakaoPayload)
        if (user == None):
            return GET_UserHome(request)

        store = storeValidation(kakaoPayload)
        menu = menuValidation(kakaoPayload)
        order = orderValidation(kakaoPayload)
        
        if(order == None or order.payment_status == IAMPORT_ORDER_STATUS_PAID):
            return errorView("Invalid Store Paratmer", "정상적이지 않은 경로거나 이미 발급이 완료되었어요!")

        order.payment_status = IAMPORT_ORDER_STATUS_PAID
        order.status = ORDER_STATUS_ORDER_CONFIRM_WAIT
        order.save()
        
        # Order Record
        try:
            orderRecordSheet = OrderRecordSheet.objects.latest('update_date')
        except OrderRecordSheet.DoesNotExist:
            orderRecordSheet = OrderRecordSheet()

        if (orderRecordSheet.timeoutValidation()):
            return kakaoView_TimeOut(KAKAO_BLOCK_SET_ORDER_SHEET)

        orderRecordSheet.user = user
        orderRecordSheet.menu = menu
        orderRecordSheet.paid = True
        orderRecordSheet.recordUpdate(ORDER_RECORD_PAYMENT_COMPLETED)

        dataActionExtra = kakaoPayload.dataActionExtra
        dataActionExtra[KAKAO_PARAM_ORDER_ID] = order.order_id
        dataActionExtra[KAKAO_PARAM_PREV_BLOCK_ID] = KAKAO_BLOCK_SET_ORDER_SHEET

        KakaoForm = Kakao_CarouselForm()
        KakaoForm.BasicCard_Init()

        thumbnail = {"imageUrl": ""}

        kakaoMapUrl = "https://map.kakao.com/link/map/{},{}".format(
            store.name, getLatLng(store.addr))

        buttons = [
            {
                'action': "webLink", 
                'label': "위치보기",
                'webLinkUrl': kakaoMapUrl
            },
            {
                'action': "block", 
                'label': "주문취소",
                'messageText': "로딩중..",
                'blockId': KAKAO_BLOCK_POST_ORDER_CANCEL,
                'extra': {
                    KAKAO_PARAM_ORDER_ID: order.order_id,
                    KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_SET_ORDER_SHEET
                }
            }
        ]

        KakaoForm.BasicCard_Add(
            "잇플패스가 발급되었습니다.",
            "주문번호: {}\n- - - - - - - - - - - - - - - - - - - - - -\n - 주문자: {}\n\n - 매장: {} \n - 메뉴: {}\n\n - 제 금액: {}원\n\n - 픽업 시간: {}\n- - - - - - - - - - - - - - - - - - - - - -\n - 매장 위치: {}".format(
                order.order_id,
                str(order.ordersheet.user.phone_number)[9:13],
                order.store.name,
                order.menu.name,
                order.totalPrice,
                dateByTimeZone(order.pickup_time).strftime('%H:%M'),
                order.store.addr
            ),
            thumbnail, buttons
        )

        QUICKREPLIES_MAP = [
            {
                'action': "block",
                'label': "홈으로 돌아가기",
                'messageText': "로딩중..",
                'blockId': KAKAO_BLOCK_HOME,
                'extra': {
                    KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_SET_ORDER_SHEET
                }
            },
        ]
        
        KakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)

        return JsonResponse(KakaoForm.GetForm())

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView("{}".format(ex))

def kakaoView_TimeOut(blockId):
    KakaoForm = Kakao_SimpleForm()
    KakaoForm.SimpleForm_Init()

    QUICKREPLIES_MAP = [
        {
            'action': "block",
            'label': "홈으로 돌아가기",
            'messageText': "로딩중..",
            'blockId': KAKAO_BLOCK_HOME,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: blockId
            }
        },
    ]

    KakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)

    KakaoForm.SimpleText_Add(
        "주문시간이 초과되었습니다."
    )

    return JsonResponse(KakaoForm.GetForm())

# # # # # # # # # # # # # # # # # # # # # # # # #
#
# External View
#
# # # # # # # # # # # # # # # # # # # # # # # # #


@csrf_exempt
def GET_Menu(request):
    EatplusSkillLog("Get Menu")

    try:
        kakaoPayload = KakaoPayLoad(request)
        return kakaoView_MenuListup(kakaoPayload)
    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView("{}".format(ex))


@csrf_exempt
def SET_PickupTime(request):
    EatplusSkillLog("Get PickupTime")


    kakaoPayload = KakaoPayLoad(request)
    return kakaoView_PickupTime(kakaoPayload)




@csrf_exempt
def SET_OrderSheet(request):
    EatplusSkillLog("Order Sheet Check")
    try:
        kakaoPayload = KakaoPayLoad(request)

        # Block Validation
        prev_block_id = prevBlockValidation(kakaoPayload)
        if(prev_block_id != KAKAO_BLOCK_SET_PICKUP_TIME and prev_block_id != KAKAO_BLOCK_SET_ORDER_SHEET):
            return errorView("Invalid Store Paratmer", "정상적이지 않은 경로거나, 오류가 발생했습니다.\n다시 주문해주세요!")

        if(prev_block_id == KAKAO_BLOCK_SET_PICKUP_TIME):
            return kakaoView_OrderPayment(kakaoPayload)
        elif(prev_block_id == KAKAO_BLOCK_SET_ORDER_SHEET):
            return kakaoView_OrderPaymentCheck(kakaoPayload)
        
    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView("{}".format(ex))

