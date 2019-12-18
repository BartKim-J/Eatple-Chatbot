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
        'action': 'block',
        'label': '홈으로 돌아가기',
        'messageText': '로딩중..',
        'blockId': KAKAO_BLOCK_USER_HOME,
        'extra': {}
    },
]


# STATIC EP_define
ORDER_LIST_LENGTH = 10

# # # # # # # # # # # # # # # # # # # # # # # # #
#
# Static View
#
# # # # # # # # # # # # # # # # # # # # # # # # #


def kakaoView_EatplePass(kakaoPayload):
    # User Validation
    user = userValidation(kakaoPayload)
    if (user == None):
        return errorView('Invalid Block Access', '정상적이지 않은 경로거나, 잘못된 계정입니다.')

    ORDER_LIST_QUICKREPLIES_MAP = [
        {
            'action': 'block',
            'label': '새로고침',
            'messageText': '로딩중..',
            'blockId': KAKAO_BLOCK_USER_EATPLE_PASS,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_EATPLE_PASS
            }
        },
        {
            'action': 'block',
            'label': '홈으로 돌아가기',
            'messageText': '로딩중..',
            'blockId': KAKAO_BLOCK_USER_HOME,
            'extra': {}
        },
    ]

    orderManager = UserOrderManager(user)
    orderManager.orderPanddingCleanUp()

    availableEatplePass = orderManager.availableOrderStatusUpdate()

    # Listup EatplePass
    if availableEatplePass:
        kakaoForm = KakaoForm()

        for order in availableEatplePass:
            thumbnail = {
                'imageUrl': '{}{}'.format(HOST_URL, '/media/STORE_DB/images/default/eatplePassImg.png'),
            }

            kakaoMapUrl = 'https://map.kakao.com/link/map/{},{}'.format(
                order.store.name,
                order.store.place
            )

            buttons = [
                {
                    'action': 'block',
                    'label': '사용하기',
                    'messageText': '로딩중..',
                    'blockId': KAKAO_BLOCK_USER_GET_USE_EATPLE_PASS_CONFIRM,
                    'extra': {
                        KAKAO_PARAM_ORDER_ID: order.order_id,
                        KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_EATPLE_PASS
                    }
                },
                {
                    'action': 'webLink',
                    'label': '위치보기',
                    'webLinkUrl': kakaoMapUrl
                },
            ]

            # CAN EDIT COUPONS
            if (order.status == ORDER_STATUS_ORDER_CONFIRM_WAIT or
                    order.status == ORDER_STATUS_ORDER_CONFIRMED):
                ORDER_LIST_QUICKREPLIES_MAP.append(
                    {
                        'action': 'block',
                        'label': '주문취소',
                        'messageText': '로딩중..',
                        'blockId': KAKAO_BLOCK_USER_POST_ORDER_CANCEL,
                        'extra': {
                            KAKAO_PARAM_ORDER_ID: order.order_id,
                            KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_EATPLE_PASS
                        }
                    }
                )
                # @PROMOTION
                if(order.type != ORDER_TYPE_PROMOTION):
                    buttons.append(
                        {
                            'action': 'block',
                            'label': '픽업시간 변경',
                            'messageText': '로딩중..',
                            'blockId': KAKAO_BLOCK_USER_EDIT_PICKUP_TIME,
                            'extra': {
                                KAKAO_PARAM_ORDER_ID: order.order_id,
                                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_EATPLE_PASS
                            }
                        }
                    )
            elif (order.status == ORDER_STATUS_PICKUP_PREPARE):
                pass
            else:
                errorView('Invalid Case on order status check by now time.')

            kakaoForm.BasicCard_Push(
                '{}'.format(order.menu.name),
                '주문번호: {}\n - 주문자: {}\n\n - 매장: {}\n - 주소: {}\n\n - 결제 금액: {}원\n\n - 픽업 시간: {}\n - 주문 상태: {}'.format(
                    order.order_id,
                    str(order.ordersheet.user.phone_number)[9:13],
                    order.store.name,
                    order.store.addr,
                    order.totalPrice,
                    dateByTimeZone(order.pickup_time).strftime(
                        '%-m월 %-d일 %p %-I시 %-M분').replace('AM', '오전').replace('PM', '오후'),
                    ORDER_STATUS[order.status][1]
                ),
                thumbnail,
                buttons
            )

        kakaoForm.BasicCard_Add()
    # No EatplePass
    else:
        kakaoForm = KakaoForm()

        kakaoForm.SimpleText_Add('현재 조회 가능한 잇플패스가 없습니다! 주문을 먼저 해주세요!')

    kakaoForm.QuickReplies_AddWithMap(ORDER_LIST_QUICKREPLIES_MAP)

    return JsonResponse(kakaoForm.GetForm())


def kakaoView_OrderDetails(kakaoPayload):
    # Block Validation
    prev_block_id = prevBlockValidation(kakaoPayload)
    if(prev_block_id != KAKAO_BLOCK_USER_HOME and prev_block_id != KAKAO_BLOCK_USER_ORDER_DETAILS):
        return errorView('Invalid Block ID', '정상적이지 않은 경로거나, 오류가 발생했습니다.\n다시 주문해주세요!')

    # User Validation
    user = userValidation(kakaoPayload)
    if (user == None):
        return errorView('Invalid Block Access', '정상적이지 않은 경로거나, 잘못된 계정입니다.')

    ORDER_LIST_QUICKREPLIES_MAP = [
        {
            'action': 'block',
            'label': '새로고침',
            'messageText': '로딩중..',
            'blockId': KAKAO_BLOCK_USER_ORDER_DETAILS,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_ORDER_DETAILS
            }
        },
        {
            'action': 'block',
            'label': '홈으로 돌아가기',
            'messageText': '로딩중..',
            'blockId': KAKAO_BLOCK_USER_HOME,
            'extra': {}
        },
    ]

    orderManager = UserOrderManager(user)
    orderManager.orderPaidCheck()

    unavailableOrders = orderManager.getUnavailableOrders()[:ORDER_LIST_LENGTH]

    if unavailableOrders:
        kakaoForm = KakaoForm()

        for order in unavailableOrders:
            thumbnail = {
                'imageUrl': ''
            }

            buttons = []

            kakaoForm.BasicCard_Push(
                '주문번호: {}'.format(order.order_id),
                ' - 주문자: {}\n\n - 매장: {} \n - 메뉴: {}\n\n - 결제 금액: {}원\n - 픽업 시간: {}\n\n - 주문 상태: {}'.format(
                    str(order.ordersheet.user.phone_number)[9:13],
                    order.store.name,
                    order.menu.name,
                    order.totalPrice,
                    dateByTimeZone(order.pickup_time).strftime(
                        '%-m월 %-d일 %p %-I시 %-M분').replace('AM', '오전').replace('PM', '오후'),
                    ORDER_STATUS[order.status][1]
                ),
                thumbnail, buttons
            )

        kakaoForm.BasicCard_Add()
    else:
        kakaoForm = KakaoForm()

        kakaoForm.SimpleText_Add('현재 조회 가능한 잇플패스가 없습니다! 주문을 먼저 해주세요!')

    kakaoForm.QuickReplies_AddWithMap(ORDER_LIST_QUICKREPLIES_MAP)

    return JsonResponse(kakaoForm.GetForm())

# # # # # # # # # # # # # # # # # # # # # # # # #
#
# External View
#
# # # # # # # # # # # # # # # # # # # # # # # # #


@csrf_exempt
def GET_OrderDetails(request):
    EatplusSkillLog('GET_OrderDetails')
    try:
        kakaoPayload = KakaoPayLoad(request)

        # User Validation
        user = userValidation(kakaoPayload)
        if (user == None):
            return GET_UserHome(request)

        return kakaoView_OrderDetails(kakaoPayload)

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView('{} '.format(ex))


@csrf_exempt
def GET_EatplePass(request):
    EatplusSkillLog('GET_EatplePass')
    try:
        kakaoPayload = KakaoPayLoad(request)

        # User Validation
        user = userValidation(kakaoPayload)
        if (user == None):
            return GET_UserHome(request)

        return kakaoView_EatplePass(kakaoPayload)

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView('{} '.format(ex))
