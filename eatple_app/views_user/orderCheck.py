# Django Library
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

# Models
from eatple_app.models import *

# Define
from eatple_app.define import *

# Modules
from eatple_app.module_kakao.reponseForm import *
from eatple_app.module_kakao.requestForm import *
from eatple_app.module_kakao.validation import *

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
ORDER_LIST_LENGTH = 4

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
            'extra': {}
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
    orderManager.orderPenddingCleanUp()

    availableEatplePass = orderManager.availableOrderStatusUpdate()
    ownEatplePass = availableEatplePass.filter(Q(ordersheet__user=user))
    delegatedEatplePass = availableEatplePass.filter(~Q(delegate=None))
    delegatedEatplePassCount = delegatedEatplePass.count()
    
    if ownEatplePass:
        nicknameList = ownEatplePass.first().ordersheet.user.nickname
    else:
        nicknameList = ''
        
    if delegatedEatplePass:
        for order in delegatedEatplePass:
            nicknameList += ', {nickname}'.format(nickname=order.ordersheet.user.nickname)
    
    # Listup EatplePass
    if ownEatplePass:
        kakaoForm = KakaoForm()

        for order in ownEatplePass:
            
            if(order.delegate != None):
                imgUrl = '{}{}'.format(HOST_URL, EATPLE_PASS_IMG_NULL)
            elif(delegatedEatplePassCount == 0):
                imgUrl = '{}{}'.format(HOST_URL, EATPLE_PASS_IMG_01)
            elif(delegatedEatplePassCount == 1):
                imgUrl = '{}{}'.format(HOST_URL, EATPLE_PASS_IMG_02)
            elif(delegatedEatplePassCount == 2):
                imgUrl = '{}{}'.format(HOST_URL, EATPLE_PASS_IMG_03)
            elif(delegatedEatplePassCount == 3):
                imgUrl = '{}{}'.format(HOST_URL, EATPLE_PASS_IMG_04)
            elif(delegatedEatplePassCount == 4):
                imgUrl = '{}{}'.format(HOST_URL, EATPLE_PASS_IMG_05) 
            else:
                imgUrl = '{}{}'.format(HOST_URL, EATPLE_PASS_IMG_MORE)
            
            thumbnail = {
                'imageUrl': imgUrl,
            }

            kakaoMapUrl = 'https://map.kakao.com/link/map/{},{}'.format(
                order.store.name,
                order.store.place
            )

            if(order.delegate != None):
                buttons = [
                ]
            else:
                buttons = [
                    {
                        'action': 'block',
                        'label': '사용하기(사장님 전용)',
                        'messageText': '로딩중..',
                        'blockId': KAKAO_BLOCK_USER_GET_USE_EATPLE_PASS_CONFIRM,
                        'extra': {
                            KAKAO_PARAM_ORDER_ID: order.order_id,
                            KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_EATPLE_PASS
                        }
                    },
                ]

            # CAN EDIT COUPONS
            if (order.status == ORDER_STATUS_ORDER_CONFIRM_WAIT or
                order.status == ORDER_STATUS_ORDER_CONFIRMED or
                order.status == ORDER_STATUS_PICKUP_PREPARE):
                
                if(order.delegate == None):
                    if(delegatedEatplePass.count() > 0):
                        ORDER_LIST_QUICKREPLIES_MAP.append(
                            {
                                'action': 'block',
                                'label': '부탁하기 전체취소',
                                'messageText': '로딩중..',
                                'blockId': KAKAO_BLOCK_USER_ORDER_SHARING_CANCEL_ALL,
                                'extra': {
                                    KAKAO_PARAM_ORDER_ID: order.order_id,
                                    KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_EATPLE_PASS
                                }
                            }
                        )
                    else:
                        buttons.append(
                            {
                                'action': 'block',
                                'label': '픽업 부탁하기',
                                'messageText': '로딩중..',
                                'blockId': KAKAO_BLOCK_USER_ORDER_SHARING_START,
                                'extra': {
                                    KAKAO_PARAM_ORDER_ID: order.order_id,
                                    KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_EATPLE_PASS
                                }
                            }
                        )
                        
                        if(order.status == ORDER_STATUS_ORDER_CONFIRM_WAIT or
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
                        if(delegatedEatplePass.count() == 0):
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
                else:
                    buttons.append(
                        {
                            'action': 'block',
                            'label': '부탁하기 취소',
                            'messageText': '로딩중..',
                            'blockId': KAKAO_BLOCK_USER_ORDER_SHARING_CANCEL,
                            'extra': {
                                KAKAO_PARAM_ORDER_ID: order.order_id,
                                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_EATPLE_PASS
                            }
                        }
                    )
            else:
                errorView('Invalid Case on order status check by now time.')

            if(order.delegate == None):
                if(delegatedEatplePass.count() > 0):
                    kakaoForm.BasicCard_Push(
                        '{}'.format(order.menu.name),
                        '주문번호: {}\n - 주문자: {}\n - 총 잇플패스 : {}개\n\n - 매장: {}\n\n - 총 금액: {}원\n\n - 픽업 시간: {}\n - 주문 상태: {}'.format(
                            order.order_id,
                            nicknameList,
                            delegatedEatplePass.count() + ownEatplePass.count(),
                            order.store.addr,
                            order.totalPrice * (delegatedEatplePass.count() + ownEatplePass.count()),
                            dateByTimeZone(order.pickup_time).strftime(
                                '%-m월 %-d일 %p %-I시 %-M분').replace('AM', '오전').replace('PM', '오후'),
                            ORDER_STATUS[order.status][1]
                        ),
                        thumbnail,
                        buttons
                    )
                else: 
                    kakaoForm.BasicCard_Push(
                        '{}'.format(order.menu.name),
                        '주문번호: {}\n - 주문자: {}({})\n\n - 매장: {}\n\n - 총 금액: {}원\n\n - 픽업 시간: {}\n - 주문 상태: {}'.format(
                            order.order_id,
                            order.ordersheet.user.nickname,
                            str(order.ordersheet.user.phone_number)[9:13],
                            order.store.name,
                            order.totalPrice,
                            dateByTimeZone(order.pickup_time).strftime(
                                '%-m월 %-d일 %p %-I시 %-M분').replace('AM', '오전').replace('PM', '오후'),
                            ORDER_STATUS[order.status][1]
                        ),
                        thumbnail,
                        buttons
                    )
            else:
                kakaoForm.BasicCard_Push(
                    '{}님에게 부탁된 잇플패스 입니다.'.format(order.delegate.nickname),
                    '주문번호: {}\n - 소유자: {}({})\n - 위임자: {}({})\n\n - 매장: {}\n - 픽업 시간: {}\n - 주문 상태: {}'.format(
                        order.order_id,
                        order.ordersheet.user.nickname,
                        str(order.ordersheet.user.phone_number)[9:13],
                        order.delegate.nickname,
                        str(order.delegate.phone_number)[9:13],
                        order.store.name,
                        dateByTimeZone(order.pickup_time).strftime(
                            '%-m월 %-d일 %p %-I시 %-M분').replace('AM', '오전').replace('PM', '오후'),
                        ORDER_STATUS[order.status][1]
                    ),
                    thumbnail,
                    buttons
                )

        kakaoForm.BasicCard_Add()
        
        if(order.delegate == None):
            kakaoForm.BasicCard_Push(
                '{}'.format(order.store.addr),
                '',
                {},
                [
                    {
                        'action': 'webLink',
                        'label': '위치보기',
                        'webLinkUrl': kakaoMapUrl
                    }
                ]
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
                'imageUrl': '{}{}'.format(HOST_URL, order.menu.imgURL()),
                'fixedRatio': 'true',
                'width': 800,
                'height': 800,
            }

            buttons = []

            kakaoForm.BasicCard_Push(
                '{}'.format(order.menu.name),
                '픽업 시간: {}\n주문 상태: {}'.format(
                    dateByTimeZone(order.pickup_time).strftime(
                        '%-m월 %-d일 %p %-I시 %-M분').replace('AM', '오전').replace('PM', '오후'),
                    ORDER_STATUS[order.status][1]
                ),
                thumbnail, buttons
            )

        kakaoForm.BasicCard_Add()
    else:
        kakaoForm = KakaoForm()

        kakaoForm.SimpleText_Add('지금까지 주문한 잇플패스가 없습니다! 어서 주문을 해보세요!')

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
