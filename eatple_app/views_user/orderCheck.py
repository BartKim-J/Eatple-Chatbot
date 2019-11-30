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


DEFAULT_QUICKREPLIES_MAP = [
    {
        'action': "block",
        'label': "홈으로 돌아가기",
        'messageText': "로딩중..",
        'blockId': KAKAO_BLOCK_HOME,
        'extra': {}
    },
]


# STATIC EP_define
ORDER_LIST_LENGTH = 10


def kakaoView_EatplePass(kakaoPayload):
    # Block Validation
    prev_block_id = prevBlockValidation(kakaoPayload)
    if(prev_block_id != KAKAO_BLOCK_HOME and prev_block_id != KAKAO_BLOCK_EATPLE_PASS):
        return errorView("nvalid Block Access", "정상적이지 않은 경로거나, 오류가 발생했습니다.\n다시 주문해주세요!")

    # User Validation
    user = userValidation(kakaoPayload)
    if (user == None):
        return GET_UserHome(request)

    ORDER_LIST_QUICKREPLIES_MAP = [
        {
            'action': "block", 
            'label': "새로고침", 
            'messageText': "로딩중..", 
            'blockId': KAKAO_BLOCK_EATPLE_PASS, 
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_EATPLE_PASS
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

    orderManager = OrderManager(user)
    orderManager.orderPaidCheck()
    
    availableEatplePass = orderManager.availableOrderStatusUpdate()

    # Listup EatplePass
    if availableEatplePass:
        KakaoForm = Kakao_CarouselForm()
        KakaoForm.BasicCard_Init()

        for order in availableEatplePass:
            thumbnail = {"imageUrl": ""}

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

            # CAN EDIT COUPONS
            if (order.status == ORDER_STATUS_PICKUP_PREPARE or 
                order.status == ORDER_STATUS_ORDER_CONFIRM_WAIT or
                order.status == ORDER_STATUS_ORDER_CONFIRMED):
                buttons.append(
                    {
                        'action': "block", 
                        'label': "주문취소",  
                        'messageText': "로딩중..",
                        'blockId': KAKAO_BLOCK_POST_ORDER_CANCEL,
                        'extra': {
                            KAKAO_PARAM_ORDER_ID: order.order_id,
                            KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_EATPLE_PASS
                        }
                    }
                )
                buttons.append(
                    {
                        'action': "block", 
                        'label': "픽업시간 변경",  
                        'messageText': "로딩중..",
                        'blockId': '',
                        'extra': {
                            KAKAO_PARAM_ORDER_ID: order.order_id,
                            KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_EATPLE_PASS
                        }
                    }
                )

            # CAN'T EDIT COUPONS
            elif (order.status == ORDER_STATUS_PICKUP_WAIT):
                buttons.append(
                    {
                        'action': "message", 
                        'label': "사용하기",  
                        'messageText': "로딩중..",
                        'blockId': '',
                        'extra': {
                            KAKAO_PARAM_ORDER_ID: order.order_id,
                            KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_EATPLE_PASS
                        }
                    }
                )
            elif (order.status == ORDER_STATUS_PICKUP_PREPARE):
                pass
            else:
                errorView("Invalid Case on order status check by now time.")
        
            KakaoForm.BasicCard_Add(
                "주문번호: {}".format(order.order_id),
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

    # No EatplePass
    else:
        KakaoForm = Kakao_SimpleForm()
        KakaoForm.SimpleForm_Init()

        ORDER_LIST_QUICKREPLIES_MAP.insert(0, {
                'action': "block", 
                'label': "메뉴보기", 
                'messageText': "로딩중..", 
                'blockId': KAKAO_BLOCK_GET_MENU,
                'extra': {
                    KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_EATPLE_PASS
                }
            }
        )

        KakaoForm.SimpleText_Add("현재 조회 가능한 잇플패스가 없습니다!\n주문하시려면 아래 [메뉴보기]를 눌러주세요!")

    KakaoForm.QuickReplies_AddWithMap(ORDER_LIST_QUICKREPLIES_MAP)
        
    return JsonResponse(KakaoForm.GetForm())


def kakaoView_OrderDetails(kakaoPayload):
    # Block Validation
    prev_block_id = prevBlockValidation(kakaoPayload)
    if(prev_block_id != KAKAO_BLOCK_HOME and prev_block_id != KAKAO_BLOCK_ORDER_DETAILS):
        return errorView("Invalid Store Paratmer", "정상적이지 않은 경로거나, 오류가 발생했습니다.\n다시 주문해주세요!")

    # User Validation
    user = userValidation(kakaoPayload)
    if (user == None):
        return GET_UserHome(request)

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

    orderManager = OrderManager(user)
    orderManager.orderPaidCheck()
    
    unavailableOrders = orderManager.getUnavailableOrders()[:ORDER_LIST_LENGTH]

    if unavailableOrders:
        KakaoForm = Kakao_CarouselForm()
        KakaoForm.BasicCard_Init()

        for order in unavailableOrders:
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
                "주문번호: {}".format(order.order_id),
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
    else:
        KakaoForm = Kakao_SimpleForm()
        KakaoForm.SimpleForm_Init()

        ORDER_LIST_QUICKREPLIES_MAP.insert(0,
            {
                'action': "block",
                'label': "메뉴보기",
                'messageText': "로딩중..",
                'blockId': KAKAO_BLOCK_GET_MENU,
                'extra': {
                    KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_ORDER_DETAILS
                }
            }
        )

        KakaoForm.SimpleText_Add("최근 주문 내역이 존재하지 않습니다!\n주문하시려면 아래 [메뉴보기]를 눌러주세요!")

    KakaoForm.QuickReplies_AddWithMap(ORDER_LIST_QUICKREPLIES_MAP)
    
    return JsonResponse(KakaoForm.GetForm())


@csrf_exempt
def GET_OrderDetails(request):
    EatplusSkillLog("GET_OrderDetails")
    try:
        kakaoPayload = KakaoPayLoad(request)
        return kakaoView_OrderDetails(kakaoPayload)

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView("{} ".format(ex))


@csrf_exempt
def GET_EatplePass(request):
    EatplusSkillLog("GET_EatplePass")
    try:
        kakaoPayload = KakaoPayLoad(request)
        return kakaoView_EatplePass(kakaoPayload)

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView("{} ".format(ex))
