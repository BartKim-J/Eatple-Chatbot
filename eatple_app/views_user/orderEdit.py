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

# # # # # # # # # # # # # # # # # # # # # # # # #
#
# Static View
#
# # # # # # # # # # # # # # # # # # # # # # # # #

def kakaoView_UseEatplePass(kakaoPayload):
    # Block Validation
    prev_block_id = prevBlockValidation(kakaoPayload)
    if(prev_block_id != KAKAO_BLOCK_USER_GET_USE_EATPLE_PASS_CONFIRM):
        return errorView('Invalid Block Access', '정상적이지 않은 경로거나, 오류가 발생했습니다.\n다시 주문해주세요!')

    # User Validation
    user = userValidation(kakaoPayload)
    if (user == None):
        return GET_UserHome(request)

    order = orderValidation(kakaoPayload)
    if(order == None or user == None):
        return errorView('Invalid Paratmer', '정상적이지 않은 주문번호이거나\n진행 중 오류가 발생했습니다.')

    if(order.status == ORDER_STATUS_PICKUP_WAIT):
        order = order.orderUsed()

        kakaoForm = KakaoForm()

        thumbnail = {
            'imageUrl': ''
        }

        buttons = [
            # No Buttons
        ]
        
        kakaoForm.BasicCard_Push(
            '잇플패스가 사용되었습니다.',
            '\n - 주문자: {}\n\n - 매장: {} \n - 메뉴: {}'.format(
                str(order.ordersheet.user.phone_number)[9:13],
                order.store.name,
                order.menu.name,
            ),
            thumbnail, buttons
        )
        kakaoForm.BasicCard_Add()
        
        QUICKREPLIES_MAP = [
            {
                'action': 'block',
                'label': '홈으로 돌아가기',
                'messageText': '로딩중..',
                'blockId': KAKAO_BLOCK_USER_HOME,
                'extra': {
                    KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_ORDER_DETAILS
                }
            },
        ]

        kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)
    else:
        kakaoForm = KakaoForm()
    
        kakaoForm.BasicCard_Push(
            ' - 주의! -', 
            '이미 사용된 잇플패스입니다. 다시 주문을 정확히 확인해주세요.', 
            {}, []
        )
        kakaoForm.BasicCard_Add()
        
        QUICKREPLIES_MAP = [
            {
                'action': 'block',
                'label': '홈으로 돌아가기',
                'messageText': '로딩중..',
                'blockId': KAKAO_BLOCK_USER_HOME,
                'extra': {
                    KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_ORDER_DETAILS
                }
            },
        ]
    
    return JsonResponse(kakaoForm.GetForm())   

def kakaoView_ConfirmUseEatplePass(kakaoPayload):
    # Block Validation
    prev_block_id = prevBlockValidation(kakaoPayload)
    if(prev_block_id != KAKAO_BLOCK_USER_EATPLE_PASS):
        return errorView('Invalid Block Access', '정상적이지 않은 경로거나, 오류가 발생했습니다.\n다시 주문해주세요!')

    # User Validation
    user = userValidation(kakaoPayload)
    if (user == None):
        return GET_UserHome(request)

    order = orderValidation(kakaoPayload)
    if(order == None or user == None):
        return errorView('Invalid Paratmer', '정상적이지 않은 주문번호이거나\n진행 중 오류가 발생했습니다.')


    if(order.status == ORDER_STATUS_PICKUP_WAIT):
        thumbnail = {
            'fixedRatio': 'true'
        }
        
        buttons = [
            {
                'action': 'block', 
                'label': '확인',    
                'messageText': '로딩중..',
                'blockId': KAKAO_BLOCK_USER_POST_USE_EATPLE_PASS, 
                'extra': {
                    KAKAO_PARAM_ORDER_ID: order.order_id,
                    KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_GET_USE_EATPLE_PASS_CONFIRM
                }
            },
            {
                'action': 'block',
                'label': '돌아가기',
                'messageText': '로딩중..',
                'blockId': KAKAO_BLOCK_USER_EATPLE_PASS,
                'extra': {
                    KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_GET_USE_EATPLE_PASS_CONFIRM
                }
            },
        ]

        kakaoForm = KakaoForm()
    
        kakaoForm.BasicCard_Push('잇플패스를 사용하시겠습니까?','', thumbnail, buttons)
        kakaoForm.BasicCard_Add()
    else:
        kakaoForm = KakaoForm()
    
        kakaoForm.BasicCard_Push(
            ' - 주의! -', 
            '이미 사용된 잇플패스입니다. 다시 주문을 정확히 확인해주세요.', 
            {}, []
        )
        kakaoForm.BasicCard_Add()
        
        QUICKREPLIES_MAP = [
            {
                'action': 'block',
                'label': '홈으로 돌아가기',
                'messageText': '로딩중..',
                'blockId': KAKAO_BLOCK_USER_HOME,
                'extra': {
                    KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_ORDER_DETAILS
                }
            },
        ]

        kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)
        
    return JsonResponse(kakaoForm.GetForm())

def kakaoView_OrderCancel(kakaoPayload):
    # Block Validation
    prev_block_id = prevBlockValidation(kakaoPayload)
    if(prev_block_id != KAKAO_BLOCK_USER_EATPLE_PASS and prev_block_id != KAKAO_BLOCK_USER_SET_ORDER_SHEET):
        return errorView('Invalid Block Access', '정상적이지 않은 경로거나, 오류가 발생했습니다.\n다시 주문해주세요!')

    # User Validation
    user = userValidation(kakaoPayload)
    if (user == None):
        return GET_UserHome(request)

    order = orderValidation(kakaoPayload)
    if(order == None):
        return errorView('Invalid Paratmer', '정상적이지 않은 주문번호이거나\n진행 중 오류가 발생했습니다.')

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
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_ORDER_DETAILS
            }
        },
    ]
    
    # EatplePass Status Update
    order.orderStatusUpdate()
    
    if (order.status == ORDER_STATUS_PICKUP_PREPARE or 
        order.status == ORDER_STATUS_ORDER_CONFIRM_WAIT or
        order.status == ORDER_STATUS_ORDER_CONFIRMED):

        response = order.orderCancel()
        if(response == False):
            return errorView('Invalid Paratmer', '정상적이지 않은 주문번호이거나\n환불 진행 중 오류가 발생했습니다.')
        
        # Cancelled EatplePass Update
        order.orderStatusUpdate()
        
        kakaoForm = KakaoForm()
        
        thumbnail = {
            'imageUrl': ''
        }

        kakaoMapUrl = 'https://map.kakao.com/link/map/{},{}'.format(
            order.store.name, 
            order.store.latlng
        )
        
        buttons = []
        
        kakaoForm.BasicCard_Push(
            '주문이 취소되었습니다.',
            ' - 주문자: {}\n\n - 매장: {} \n - 메뉴: {}\n\n - 결제 금액: {}원\n - 픽업 시간: {}\n\n - 주문 상태: {}'.format(
                str(order.ordersheet.user.phone_number)[9:13],
                order.store.name,
                order.menu.name,
                order.totalPrice,
                dateByTimeZone(order.pickup_time).strftime('%p %-I시 %-M분 %-m월 %-d일').replace('AM','오전').replace('PM','오후') ,
                ORDER_STATUS[order.status][1]
            ),
            thumbnail, buttons
        )
        kakaoForm.BasicCard_Add()
        
        QUICKREPLIES_MAP = [
            {
                'action': 'block',
                'label': '홈으로 돌아가기',
                'messageText': '로딩중..',
                'blockId': KAKAO_BLOCK_USER_HOME,
                'extra': {
                    KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_ORDER_DETAILS
                }
            },
        ]

        kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)
        
        return JsonResponse(kakaoForm.GetForm())
    
    else:
        return errorView('Invalid Paratmer', '정상적이지 않은 주문번호이거나\n진행 중 오류가 발생했습니다.')

def kakaoView_EditPickupTime(kakaoPayload):
    # Block Validation
    prev_block_id = prevBlockValidation(kakaoPayload)
    if(prev_block_id != KAKAO_BLOCK_USER_EATPLE_PASS):
        return errorView('Invalid Block Access', '정상적이지 않은 경로거나, 오류가 발생했습니다.\n다시 주문해주세요!')

    # User Validation
    user = userValidation(kakaoPayload)
    if (user == None):
        return GET_UserHome(request)

    order = orderValidation(kakaoPayload)
    if(order == None):
        return errorView('Invalid Paratmer', '정상적이지 않은 주문번호이거나\n진행 중 오류가 발생했습니다.')

    menu = order.menu
    store = order.store
        
    currentSellingTime = order.menu.sellingTime

    kakaoForm = KakaoForm()

    kakaoForm.SimpleText_Add(
        '음식을 가지러 갈 픽업시간을 설정해주세요.'
    )

    PICKUP_TIME_QUICKREPLIES_MAP = []

    pickupTimes = menu.pickupTime.all()

    order = orderValidation(kakaoPayload)

    for pickupTime in pickupTimes:
        dataActionExtra = {
            KAKAO_PARAM_ORDER_ID: order.order_id,
            KAKAO_PARAM_PICKUP_TIME: pickupTime.time.strftime('%H:%M'),
            KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_EDIT_PICKUP_TIME
        }

        kakaoForm.QuickReplies_Add(
            'block',
            pickupTime.time.strftime('%H:%M'),
            '로딩중..',
            KAKAO_BLOCK_USER_EDIT_PICKUP_TIME_CONFIRM,
            dataActionExtra
        )

    return JsonResponse(kakaoForm.GetForm())

def kakaoView_ConfirmEditPickupTime(kakaoPayload):
    # Block Validation
    prev_block_id = prevBlockValidation(kakaoPayload)
    if(prev_block_id != KAKAO_BLOCK_USER_EDIT_PICKUP_TIME):
        return errorView('Invalid Block Access', '정상적이지 않은 경로거나, 오류가 발생했습니다.\n다시 주문해주세요!')

    # User Validation
    user = userValidation(kakaoPayload)
    if (user == None):
        return GET_UserHome(request)

    order = orderValidation(kakaoPayload)
    pickup_time = pickupTimeValidation(kakaoPayload)

    if(order == None and pickupTimeValidation == None):
        return errorView('Invalid Paratmer', '정상적이지 않은 주문번호이거나\n진행 중 오류가 발생했습니다.')

    beforePickupTime = order.pickup_time
    order.pickup_time = order.pickupTimeToDateTime(pickup_time)
    order.save()

    kakaoForm = KakaoForm()

    thumbnail = {
        'imageUrl': ''
    }

    buttons = [
        # No Buttons
    ]


    kakaoForm.BasicCard_Push(
        '픽업타임이 변경되었습니다.',
        ' - 주문자: {}\n\n - 매장: {} \n - 메뉴: {}\n\n - 결제 금액: {}원\n - 픽업 시간: {}\n\n - 주문 상태: {}'.format(
            str(order.ordersheet.user.phone_number)[9:13],
            order.store.name,
            order.menu.name,
            order.totalPrice,
            dateByTimeZone(order.pickup_time).strftime('%p %-I시 %-M분 %-m월 %-d일').replace('AM','오전').replace('PM','오후') ,
            ORDER_STATUS[order.status][1]
        ),
        thumbnail, buttons
    )
    kakaoForm.BasicCard_Add()
    
    QUICKREPLIES_MAP = [
        {
            'action': 'block',
            'label': '홈으로 돌아가기',
            'messageText': '로딩중..',
            'blockId': KAKAO_BLOCK_USER_HOME,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_ORDER_DETAILS
            }
        },
    ]

    kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)

    return JsonResponse(kakaoForm.GetForm())
    
# # # # # # # # # # # # # # # # # # # # # # # # #
#
# External View
#
# # # # # # # # # # # # # # # # # # # # # # # # #

@csrf_exempt
def GET_EditPickupTime(request):
    EatplusSkillLog('GET_EditPickupTime')
    try:
        kakaoPayload = KakaoPayLoad(request)
        return kakaoView_EditPickupTime(kakaoPayload)

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView('{}'.format(ex))

@csrf_exempt
def SET_ConfirmEditPickupTime(request):
    EatplusSkillLog('SET_ConfirmEditPickupTime')
    try:
        kakaoPayload = KakaoPayLoad(request)
        return kakaoView_ConfirmEditPickupTime(kakaoPayload)

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView('{}'.format(ex))


@csrf_exempt
def GET_ConfirmUseEatplePass(request):
    EatplusSkillLog('GET_ConfirmUseEatplePass')
    try:
        kakaoPayload = KakaoPayLoad(request)
        return kakaoView_ConfirmUseEatplePass(kakaoPayload)

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView('{} '.format(ex))

@csrf_exempt
def POST_UseEatplePass(request):
    EatplusSkillLog('POST_UserEatplePass')
    try:
        kakaoPayload = KakaoPayLoad(request)
        return kakaoView_UseEatplePass(kakaoPayload)

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView('{}'.format(ex))


@csrf_exempt
def POST_OrderCancel(request):
    EatplusSkillLog('POST_OrderCancel')

    try:
        kakaoPayload = KakaoPayLoad(request)
        return kakaoView_OrderCancel(kakaoPayload)

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView('{}'.format(ex))

