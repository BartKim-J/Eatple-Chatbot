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

DEFAULT_QUICKREPLIES_MAP = [
    {
        'action': "block",
        'label': "홈으로 돌아가기",
        'messageText': "로딩중..",
        'blockId': KAKAO_BLOCK_HOME,
        'extra': {}
    },
]

# # # # # # # # # # # # # # # # # # # # # # # # #
#
# Static View
#
# # # # # # # # # # # # # # # # # # # # # # # # #

def kakaoView_UseEatplePass(kakaoPayload):
    # Invalied Path Access
    if (kakaoPayload.orderID == NOT_APPLICABLE):
        return errorView("Parameter Invalid")
    else:
        orderInstance = Order.objects.get(id=kakaoPayload.orderID)

    EatplusSkillLog("Order Change Flow")

    orderInstance.status = ORDER_STATUS[ORDER_STATUS_DICT['픽업 완료']][0]
    orderInstance.save()

    KakaoForm = Kakao_CarouselForm()
    KakaoForm.BasicCard_Init()

    thumbnail = {"imageUrl": ""}

    kakaoMapUrl = "https://map.kakao.com/link/map/{},{}".format(
        orderInstance.storeInstance.name, getLatLng(orderInstance.storeInstance.addr))

    buttons = [
        # No Buttons
    ]

    KakaoForm.BasicCard_Add(
        "잇플패스가 사용되었습니다.",
        "주문번호: {}\n--------------------\n - 주문자: {}\n\n - 매장: {} \n - 메뉴: {}\n\n - 결제 금액: {}원\n\n - 픽업 시간: {}\n--------------------".format(
            orderInstance.management_code,
            orderInstance.userInstance.name,
            orderInstance.storeInstance.name,
            orderInstance.menuInstance.name,
            orderInstance.menuInstance.price,
            orderInstance.pickupTime.astimezone().strftime('%H시%M분 %m월%d일'),
        ),
        thumbnail, buttons
    )

    for entryPoint in DEFAULT_QUICKREPLIES_MAP:
        KakaoForm.QuickReplies_Add(entryPoint['action'], entryPoint['label'],
                                    entryPoint['messageText'], entryPoint['blockId'], entryPoint['extra'])

    return JsonResponse(KakaoForm.GetForm())   

def kakaoView_OrderCancel(kakaoPayload):
    # Block Validation
    prev_block_id = prevBlockValidation(kakaoPayload)
    if(prev_block_id != KAKAO_BLOCK_EATPLE_PASS and prev_block_id != KAKAO_BLOCK_SET_ORDER_SHEET):
        return errorView("Invalid Block Access", "정상적이지 않은 경로거나, 오류가 발생했습니다.\n다시 주문해주세요!")

    # User Validation
    user = userValidation(kakaoPayload)
    if (user == None):
        return GET_UserHome(request)

    order = orderValidation(kakaoPayload)
    if(order == None or user == None):
        return errorView("Invalid Paratmer", "정상적이지 않은 주문번호이거나\n진행 중 오류가 발생했습니다.")

    ORDER_LIST_QUICKREPLIES_MAP = [
        {
            'action': "block",
            'label': "새로고침",
            'messageText': "로딩중..",
            'blockId': KAKAO_BLOCK_ORDER_DETAILS,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_ORDER_DETAILS
            }
        },
        {
            'action': "block",
            'label': "홈으로 돌아가기",
            'messageText': "로딩중..",
            'blockId': KAKAO_BLOCK_HOME,
            'extra': {}
        },
    ]
    
    # EatplePass Status Update
    orderManager = OrderManager(user)
    orderManager.orderStatusUpdate(order)
    
    if (order.status == ORDER_STATUS_PICKUP_PREPARE or 
        order.status == ORDER_STATUS_ORDER_CONFIRM_WAIT or
        order.status == ORDER_STATUS_ORDER_CONFIRMED):
        iamport = Iamport(imp_key=IAMPORT_API_KEY, imp_secret=IAMPORT_API_SECRET_KEY)

        try:
            response = iamport.cancel('주문 취소', merchant_uid=order.order_id)    
        except (KeyError, Iamport.ResponseError, Iamport.HttpError):
            try:
                response = iamport.find(merchant_uid=order.order_id)
            except (KeyError, Iamport.ResponseError):
                return errorView("Invalid Paratmer", "정상적이지 않은 주문번호이거나\n진행 중 오류가 발생했습니다.")
            except Iamport.HttpError as http_error:
                return errorView("Invalid Paratmer", "정상적이지 않은 주문번호이거나\n진행 중 오류가 발생했습니다.")
                
        except Iamport.HttpError as http_error:
            print(response)
            return errorView("Invalid Paratmer", "정상적이지 않은 주문번호이거나\n진행 중 오류가 발생했습니다.")
        
        
        
        if(response['status'] == IAMPORT_ORDER_STATUS_CANCLED):
            order.payment_status = response['status']
            order.status = ORDER_STATUS_ORDER_CANCELED
            order.save()

        else:
            return errorView("Invalid Paratmer", "진행 중 오류가 발생했습니다.\n다시 환불 신청을 해주세요.")
        
        KakaoForm = Kakao_CarouselForm()
        KakaoForm.BasicCard_Init()
        
        thumbnail = {
            "imageUrl": ""
        }

        kakaoMapUrl = "https://map.kakao.com/link/map/{},{}".format(
            order.store.name, 
            getLatLng(order.store.addr)
        )
        
        buttons = [
            {
                'action': "webLink", 
                'label': "위치보기",  
                "webLinkUrl": kakaoMapUrl
            },
        ]
        
        KakaoForm.BasicCard_Add(
            "주문이 취소되었습니다.",
            " - 주문자: {}\n\n - 매장: {} \n - 메뉴: {}\n\n - 결제 금액: {}원\n - 픽업 시간: {}\n\n - 주문 상태: {}".format(
                str(order.ordersheet.user.phone_number)[9:13],
                order.store.name,
                order.menu.name,
                order.totalPrice,
                order.pickup_time,
                ORDER_STATUS[order.status][1]
            ),
            thumbnail, buttons
        )

        for entryPoint in DEFAULT_QUICKREPLIES_MAP:
            KakaoForm.QuickReplies_Add(entryPoint['action'], entryPoint['label'],
                                        entryPoint['messageText'], entryPoint['blockId'], entryPoint['extra'])
        
        return JsonResponse(KakaoForm.GetForm())
    
    else:
        return errorView("Invalid Paratmer", "정상적이지 않은 주문번호이거나\n진행 중 오류가 발생했습니다.")

# # # # # # # # # # # # # # # # # # # # # # # # #
#
# External View
#
# # # # # # # # # # # # # # # # # # # # # # # # #

@csrf_exempt
def GET_PickupTimeForChange(request):
    try:
        kakaoPayload = KakaoPayLoad(request)

        # Invalied Path Access
        if(kakaoPayload.orderID == NOT_APPLICABLE) or (kakaoPayload.sellingTime == NOT_APPLICABLE):
            return errorView("Parameter Invalid")
        else:
            orderInstance = Order.objects.get(id=kakaoPayload.orderID)

        EatplusSkillLog("Order Change Flow")

        KakaoForm = Kakao_SimpleForm()
        KakaoForm.SimpleForm_Init()

        KakaoForm.SimpleText_Add("변경 하실 픽업 시간을 설정해주세요.")

        allExtraData = kakaoPayload.dataActionExtra

        PICKUP_TIME_QUICKREPLIES_MAP = []

        if SELLING_TIME_CATEGORY_DICT[kakaoPayload.sellingTime] == SELLING_TIME_LUNCH:
            ENTRY_PICKUP_TIME_MAP = LUNCH_PICKUP_TIME
            pikcupTime_Start = orderInstance.storeInstance.lunch_pickupTime_start
            pikcupTime_End = orderInstance.storeInstance.lunch_pickupTime_end
        else:
            ENTRY_PICKUP_TIME_MAP = DINNER_PICKUP_TIME
            pikcupTime_Start = orderInstance.storeInstance.dinner_pickupTime_start
            pikcupTime_End = orderInstance.storeInstance.dinner_pickupTime_end

        for index, pickupTime in ENTRY_PICKUP_TIME_MAP:
            if(pikcupTime_Start <= index) and (index <= pikcupTime_End):
                PICKUP_TIME_QUICKREPLIES_MAP += {'action': "message", 'label': pickupTime, 'messageText': wordings.ORDER_PICKUP_TIME_CHANGE_CONFIRM_COMMAND,
                                                 'blockId': "none", 'extra': {**allExtraData, KAKAO_PARAM_PICKUP_TIME: pickupTime}},

        for entryPoint in PICKUP_TIME_QUICKREPLIES_MAP:
            KakaoForm.QuickReplies_Add(entryPoint['action'], entryPoint['label'],
                                       entryPoint['messageText'], entryPoint['blockId'], entryPoint['extra'])

        return JsonResponse(KakaoForm.GetForm())

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView("{}".format(ex))

@csrf_exempt
def SET_PickupTimeByChanged(request):
    try:
        kakaoPayload = KakaoPayLoad(request)

        # Invalied Path Access
        if (kakaoPayload.orderID == NOT_APPLICABLE) or kakaoPayload.pickupTime == NOT_APPLICABLE:
            return errorView("Parameter Invalid")
        else:
            orderInstance = Order.objects.get(id=kakaoPayload.orderID)

        EatplusSkillLog("Order Change Flow")

        beforePickupTime = orderInstance.pickupTime
        orderInstance.pickupTime = orderInstance.rowPickupTimeToDatetime(
            kakaoPayload.pickupTime).replace(day=beforePickupTime.day)
        orderInstance.save()

        KakaoForm = Kakao_CarouselForm()
        KakaoForm.BasicCard_Init()

        thumbnail = {"imageUrl": ""}

        kakaoMapUrl = "https://map.kakao.com/link/map/{},{}".format(
            orderInstance.storeInstance.name, getLatLng(orderInstance.storeInstance.addr))

        buttons = [
            {'action': "webLink", 'label': wordings.SHOW_LOCATION_BTN,
                "webLinkUrl": kakaoMapUrl},
        ]

        KakaoForm.BasicCard_Add(
            "{}시 {}분으로 변경되었습니다.".format(orderInstance.pickupTime.astimezone().strftime(
                '%H'), orderInstance.pickupTime.astimezone().strftime('%M')),
            "주문번호: {}\n--------------------\n - 주문자: {}\n\n - 매장: {} \n - 메뉴: {}\n\n - 결제 금액: {}원\n\n - 픽업 시간: {}\n--------------------".format(
                orderInstance.management_code,
                orderInstance.userInstance.name,
                orderInstance.storeInstance.name,
                orderInstance.menuInstance.name,
                orderInstance.menuInstance.price,
                orderInstance.pickupTime.astimezone().strftime('%H시%M분 %m월%d일'),
            ),
            thumbnail, buttons
        )

        for entryPoint in DEFAULT_QUICKREPLIES_MAP:
            KakaoForm.QuickReplies_Add(entryPoint['action'], entryPoint['label'],
                                       entryPoint['messageText'], entryPoint['blockId'], entryPoint['extra'])

        return JsonResponse(KakaoForm.GetForm())

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView("{}".format(ex))


@csrf_exempt
def GET_ConfirmUserCoupon(request):
    try:
        kakaoPayload = KakaoPayLoad(request)

        # Invalied Path Access
        if(kakaoPayload.orderID == NOT_APPLICABLE):
            return errorView("Parameter Invalid")
        else:
            try:
                userInstance = User.objects.get(
                    identifier_code=kakaoPayload.userID)
            except User.DoesNotExist:
                return errorView("User ID is Invalid")

            OrderInstance = Order.objects.get(id=kakaoPayload.orderID)

        USE_COUPON_QUICKREPLIES_MAP = [
            {'action': "message", 'label': "사용하기",    'messageText': wordings.USE_COUPON_COMMAND,
                'blockId': "none", 'extra': {KAKAO_PARAM_ORDER_ID: OrderInstance.id}},
            {'action': "message", 'label': wordings.RETURN_HOME_QUICK_REPLISE,    'messageText': wordings.RETURN_HOME_QUICK_REPLISE,
                'blockId': "none", 'extra': {}},
        ]

        EatplusSkillLog("Order Check Flow")

        KakaoForm = Kakao_SimpleForm()
        KakaoForm.SimpleForm_Init()

        thumbnail = {"imageUrl": ""}

        buttons = [
            # No Buttons
        ]

        KakaoForm.SimpleText_Add("잇플패스를 사용하시겠습니까?")

        for entryPoint in USE_COUPON_QUICKREPLIES_MAP:
            KakaoForm.QuickReplies_Add(entryPoint['action'], entryPoint['label'],
                                       entryPoint['messageText'], entryPoint['blockId'], entryPoint['extra'])

        return JsonResponse(KakaoForm.GetForm())

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView("{} ".format(ex))



@csrf_exempt
def POST_UseCoupon(request):
    EatplusSkillLog("POST_UserEatplePass")
    try:
        kakaoPayload = KakaoPayLoad(request)
        return kakaoView_UseEatplePass(kakaoPayload)

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView("{}".format(ex))


@csrf_exempt
def POST_OrderCancel(request):
    EatplusSkillLog("POST_OrderCancel")

    kakaoPayload = KakaoPayLoad(request)
    return kakaoView_OrderCancel(kakaoPayload)

