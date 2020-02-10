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
        return errorView('잘못된 블럭 경로', '정상적이지 않은 경로거나, 오류가 발생했습니다.\n다시 주문해주세요!')

    # User Validation
    user = userValidation(kakaoPayload)
    if (user == None):
        return errorView('잘못된 블럭 경로', '정상적이지 않은 경로거나, 잘못된 계정입니다.')

    order = orderValidation(kakaoPayload)
    if(order == None):
        return errorView('Invalid Paratmer', '정상적이지 않은 주문번호이거나\n진행 중 오류가 발생했습니다.')
    else:
        order.orderStatusUpdate()

    orderManager = UserOrderManager(user)

    availableEatplePass = orderManager.availableOrderStatusUpdate()
    delegatedEatplePass = availableEatplePass.filter(~Q(delegate=None))
    
    kakaoForm = KakaoForm()

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

    if(order.status == ORDER_STATUS_PICKUP_WAIT):
        order = order.orderUsed()
        
        if delegatedEatplePass:
            for delegatedOrder in delegatedEatplePass:
                delegatedOrder = delegatedOrder.orderUsed()
                
        thumbnail = {
            'imageUrl': ''
        }

        buttons = [
            # No Buttons
        ]

        kakaoForm.BasicCard_Push(
            '잇플패스가 사용되었습니다.',
            '\n - 주문자: {}({})\n\n - 매장: {} \n - 메뉴: {}'.format(
                order.ordersheet.user.nickname,
                str(order.ordersheet.user.phone_number)[9:13],
                order.store.name,
                order.menu.name,
            ),
            thumbnail, buttons
        )
        kakaoForm.BasicCard_Add()

        kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)
    elif(order.status == ORDER_STATUS_PICKUP_COMPLETED):

        kakaoForm.BasicCard_Push(
            ' - 주의! -',
            '이미 사용된 잇플패스입니다. 다시 주문을 확인해주세요.',
            {}, []
        )
        kakaoForm.BasicCard_Add()

        kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)
    elif(order.status == ORDER_STATUS_ORDER_EXPIRED):
        kakaoForm.BasicCard_Push(
            ' - 주의! -',
            '이미 만료된 잇플패스입니다. 다시 주문을 확인해주세요.',
            {}, []
        )
        kakaoForm.BasicCard_Add()

        kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)
    else:
        kakaoForm.BasicCard_Push(
            '사용 가능한 픽업 시간이 아닙니다!',
            '잇플패스의 픽업 시간을 확인해주세요!',
            {}, []
        )
        kakaoForm.BasicCard_Add()

        kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)

    return JsonResponse(kakaoForm.GetForm())


def kakaoView_ConfirmUseEatplePass(kakaoPayload):
    # User Validation
    user = userValidation(kakaoPayload)
    if (user == None):
        return errorView('잘못된 블럭 경로', '정상적이지 않은 경로거나, 잘못된 계정입니다.')

    order = orderValidation(kakaoPayload)
    if(order == None):
        return errorView('Invalid Paratmer', '정상적이지 않은 주문번호이거나\n진행 중 오류가 발생했습니다.')
    else:
        order.orderStatusUpdate()

    orderManager = UserOrderManager(user)
    orderManager.orderPenddingCleanUp()

    availableEatplePass = orderManager.availableOrderStatusUpdate()
    ownEatplePass = availableEatplePass.filter(Q(delegate=None))
    delegatedEatplePass = availableEatplePass.filter(~Q(delegate=None))
    
    kakaoForm = KakaoForm()

    QUICKREPLIES_MAP = [
        {
            'action': 'block',
            'label': '홈으로 돌아가기',
            'messageText': '로딩중..',
            'blockId': KAKAO_BLOCK_USER_HOME,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_GET_USE_EATPLE_PASS_CONFIRM
            }
        },
        {
            'action': 'block',
            'label': '새로고침',
            'messageText': '로딩중..',
            'blockId': KAKAO_BLOCK_USER_EATPLE_PASS,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_GET_USE_EATPLE_PASS_CONFIRM
            }
        },
    ]

    if(order.delegate != None):
        kakaoForm.BasicCard_Push(
            '타인에게 부탁한 잇플패스는 사용이 불가능합니다.',
            '사용하시고 싶다면 \'부탁하기 취소\'를 한 다음 사용해주세요!',
            {}, []
        )
        kakaoForm.BasicCard_Add()

        kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)
        
        return JsonResponse(kakaoForm.GetForm())
    
    
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
        
        if delegatedEatplePass:
            kakaoForm.BasicCard_Push(
                '총 {}개의 잇플패스를 사용하시겠습니까?'.format(delegatedEatplePass.count() + ownEatplePass.count()),
                '부탁받은 잇플패스를 포함하여 전부 사용하게됩니다.',
                thumbnail,
                buttons
            )
            kakaoForm.BasicCard_Add()
        else:
            kakaoForm.BasicCard_Push(
                '잇플패스를 사용하시겠습니까?',
                '사용한 이후에는 취소/환불이 불가능합니다.',
                thumbnail,
                buttons
            )
            kakaoForm.BasicCard_Add()
            
    elif(order.status == ORDER_STATUS_PICKUP_COMPLETED):

        kakaoForm.BasicCard_Push(
            ' - 주의! -',
            '이미 사용된 잇플패스입니다. 다시 주문을 정확히 확인해주세요.',
            {}, []
        )
        kakaoForm.BasicCard_Add()

        kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)
    else:
        kakaoForm.BasicCard_Push(
            '사용 가능한 픽업 시간이 아닙니다!',
            '잇플패스의 픽업 시간을 확인해주세요!',
            {}, []
        )
        kakaoForm.BasicCard_Add()

        kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)
    return JsonResponse(kakaoForm.GetForm())


def kakaoView_OrderCancel(kakaoPayload):
    # Block Validation
    prev_block_id = prevBlockValidation(kakaoPayload)
    if(prev_block_id != KAKAO_BLOCK_USER_EATPLE_PASS and prev_block_id != KAKAO_BLOCK_USER_SET_ORDER_SHEET):
        return errorView('잘못된 블럭 경로', '정상적이지 않은 경로거나, 오류가 발생했습니다.\n다시 주문해주세요!')

    # User Validation
    user = userValidation(kakaoPayload)
    if (user == None):
        return errorView('잘못된 블럭 경로', '정상적이지 않은 경로거나, 잘못된 계정입니다.')

    order = orderValidation(kakaoPayload)
    if(order == None):
        return errorView('Invalid Paratmer', '정상적이지 않은 주문번호이거나\n진행 중 오류가 발생했습니다.')
    else:
        order.orderStatusUpdate()

    QUICKREPLIES_MAP = [
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
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_EATPLE_PASS
            }
        },
    ]


    kakaoForm = KakaoForm()
    
    if (order.status == ORDER_STATUS_ORDER_CONFIRM_WAIT or
            order.status == ORDER_STATUS_ORDER_CONFIRMED):

        response = order.orderCancel()
        if(response == False):
            return errorView('Invalid Paratmer', '정상적이지 않은 주문번호이거나\n환불 진행 중 오류가 발생했습니다.')

        # Cancelled EatplePass Update
        order.orderDelegateCancel()
        order.orderStatusUpdate()

        thumbnail = {
            'imageUrl': ''
        }

        kakaoMapUrl = 'https://map.kakao.com/link/map/{},{}'.format(
            order.store.name,
            order.store.place
        )

        buttons = []

        kakaoForm.BasicCard_Push(
            '주문이 취소되었습니다.',
            ' - 주문자: {}({})\n\n - 매장: {} \n - 메뉴: {}\n\n - 총 금액: {}원\n - 픽업 시간: {}\n\n - 주문 상태: {}'.format(
                order.ordersheet.user.nickname,
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

        kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)

        return JsonResponse(kakaoForm.GetForm())

    else:
        kakaoForm.BasicCard_Push(
            '현재는 주문을 취소 할 수 없는 시간입니다.',
            '환불/취소 가능 시간 : 픽업 당일 오전 10시 30분까지',
            {},
            []
        )
        kakaoForm.BasicCard_Add()

        kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)

        return JsonResponse(kakaoForm.GetForm())


def kakaoView_EditPickupTime(kakaoPayload):
    # Block Validation
    prev_block_id = prevBlockValidation(kakaoPayload)
    if(prev_block_id != KAKAO_BLOCK_USER_EATPLE_PASS):
        return errorView('잘못된 블럭 경로', '정상적이지 않은 경로거나, 오류가 발생했습니다.\n다시 주문해주세요!')

    # User Validation
    user = userValidation(kakaoPayload)
    if (user == None):
        return errorView('잘못된 블럭 경로', '정상적이지 않은 경로거나, 잘못된 계정입니다.')

    order = orderValidation(kakaoPayload)
    if(order == None):
        return errorView('Invalid Paratmer', '정상적이지 않은 주문번호이거나\n진행 중 오류가 발생했습니다.')
    else:
        order.orderStatusUpdate()
        
    menu = order.menu
    store = order.store

    currentSellingTime = order.menu.selling_time

    kakaoForm = KakaoForm()

    QUICKREPLIES_MAP = [
        {
            'action': 'block',
            'label': '홈으로 돌아가기',
            'messageText': '로딩중..',
            'blockId': KAKAO_BLOCK_USER_HOME,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_EDIT_PICKUP_TIME
            }
        },
    ]
    
    if(order.payment_status == IAMPORT_ORDER_STATUS_CANCELLED):
        kakaoForm.BasicCard_Push(
            '이 잇플 패스는 이미 취소된 잇플 패스입니다.',
            '다시 주문을 확인해주세요.',
            {}, 
            []
        )
        kakaoForm.BasicCard_Add()

        kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)

        return JsonResponse(kakaoForm.GetForm())

    if (order.status != ORDER_STATUS_ORDER_CONFIRM_WAIT and
        order.status != ORDER_STATUS_ORDER_CONFIRMED):
        kakaoForm.BasicCard_Push(
            '현재는 픽업시간을 변경 할 수 없는 시간입니다.',
            '변경 가능 시간 : 픽업 당일 오전 10시 30분까지',
            {}, 
            []
        )
        kakaoForm.BasicCard_Add()

        kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)

        return JsonResponse(kakaoForm.GetForm())

    kakaoForm.BasicCard_Push(
        '변경할 픽업시간을 선택해주세요.',
        ' - 현재 픽업시간 : {}'.format(
            dateByTimeZone(order.pickup_time).strftime('%p %-I시 %-M분').replace('AM', '오전').replace('PM', '오후'),),
        {},
        []
    )
    kakaoForm.BasicCard_Add()

    PICKUP_TIME_QUICKREPLIES_MAP = []

    pickupTimes = menu.pickup_time.all()

    order = orderValidation(kakaoPayload)

    for pickupTime in pickupTimes:
        if(
            order.pickupTimeToDateTime(str(pickupTime.time)).strftime('%p %-I시 %-M분') == 
            dateByTimeZone(order.pickup_time).strftime('%p %-I시 %-M분')
           ):
            pass
        else:
            dataActionExtra = {
                KAKAO_PARAM_ORDER_ID: order.order_id,
                KAKAO_PARAM_PICKUP_TIME: pickupTime.time.strftime('%H:%M'),
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_EDIT_PICKUP_TIME
            }

            kakaoForm.QuickReplies_Add(
                'block',
                pickupTime.time.strftime(
                    '%p %-I시 %-M분').replace('AM', '오전').replace('PM', '오후'),
                '로딩중..',
                KAKAO_BLOCK_USER_EDIT_PICKUP_TIME_CONFIRM,
                dataActionExtra
            )

    kakaoForm.QuickReplies_Add(
        'block',
        '돌아가기',
        '로딩중..',
        KAKAO_BLOCK_USER_EATPLE_PASS,
        {
            KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_EDIT_PICKUP_TIME_CONFIRM
        }        
    )

    return JsonResponse(kakaoForm.GetForm())


def kakaoView_ConfirmEditPickupTime(kakaoPayload):
    # Block Validation
    prev_block_id = prevBlockValidation(kakaoPayload)
    if(prev_block_id != KAKAO_BLOCK_USER_EDIT_PICKUP_TIME):
        return errorView('잘못된 블럭 경로', '정상적이지 않은 경로거나, 오류가 발생했습니다.\n다시 주문해주세요!')

    # User Validation
    user = userValidation(kakaoPayload)
    if (user == None):
        return errorView('잘못된 블럭 경로', '정상적이지 않은 경로거나, 잘못된 계정입니다.')

    order = orderValidation(kakaoPayload)
    if(order == None and pickupTimeValidation == None):
        return errorView('Invalid Paratmer', '정상적이지 않은 주문번호이거나\n진행 중 오류가 발생했습니다.')
    else:
        order.orderStatusUpdate()
    
    pickup_time = pickupTimeValidation(kakaoPayload)

    beforePickupTime = dateByTimeZone(order.pickup_time)
    order.pickup_time = order.pickupTimeToDateTime(pickup_time)
    order.save()

    kakaoForm = KakaoForm()

    QUICKREPLIES_MAP = [
        {
            'action': 'block',
            'label': '홈으로 돌아가기',
            'messageText': '로딩중..',
            'blockId': KAKAO_BLOCK_USER_HOME,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_EDIT_PICKUP_TIME
            }
        },
    ]

    if(order.status == ORDER_STATUS_ORDER_CANCELED):
        kakaoForm.BasicCard_Push(
            '이 잇플패스는 이미 취소된 잇플패스입니다.',
            '다시 주문을 확인해주세요.',
            {}, []
        )
        kakaoForm.BasicCard_Add()

        kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)

        return JsonResponse(kakaoForm.GetForm())

    if (order.status != ORDER_STATUS_ORDER_CONFIRM_WAIT and
            order.status != ORDER_STATUS_ORDER_CONFIRMED):
        kakaoForm.BasicCard_Push(
            '현재는 픽업시간을 변경 할 수 없는 시간입니다.',
            '변경 가능 시간 : 픽업 당일 오전 10시 30분까지',
            {}, 
            []
        )
        kakaoForm.BasicCard_Add()

        kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)

        return JsonResponse(kakaoForm.GetForm())

    thumbnail = {
        'imageUrl': ''
    }

    buttons = [
        # No Buttons
    ]

    kakaoForm.BasicCard_Push(
        '픽업타임이 변경되었습니다.',
        '{}  ➔  {}'.format(
            beforePickupTime.strftime(
                '%p %-I시 %-M분').replace('AM', '오전').replace('PM', '오후'),
            order.pickup_time.strftime(
                '%p %-I시 %-M분').replace('AM', '오전').replace('PM', '오후'),
        ),
        thumbnail, buttons
    )
    kakaoForm.BasicCard_Add()

    QUICKREPLIES_MAP = [
        {
            'action': 'block',
            'label': '돌아가기',
            'messageText': '로딩중..',
            'blockId': KAKAO_BLOCK_USER_EATPLE_PASS,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_EDIT_PICKUP_TIME_CONFIRM
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

        # User Validation
        user = userValidation(kakaoPayload)
        if (user == None):
            return GET_UserHome(request)

        return kakaoView_EditPickupTime(kakaoPayload)

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView('{}'.format(ex))


@csrf_exempt
def SET_ConfirmEditPickupTime(request):
    EatplusSkillLog('SET_ConfirmEditPickupTime')
    try:
        kakaoPayload = KakaoPayLoad(request)

        # User Validation
        user = userValidation(kakaoPayload)
        if (user == None):
            return GET_UserHome(request)

        return kakaoView_ConfirmEditPickupTime(kakaoPayload)

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView('{}'.format(ex))


@csrf_exempt
def GET_ConfirmUseEatplePass(request):
    EatplusSkillLog('GET_ConfirmUseEatplePass')
    try:
        kakaoPayload = KakaoPayLoad(request)

        # User Validation
        user = userValidation(kakaoPayload)
        if (user == None):
            return GET_UserHome(request)

        return kakaoView_ConfirmUseEatplePass(kakaoPayload)

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView('{} '.format(ex))


@csrf_exempt
def POST_UseEatplePass(request):
    EatplusSkillLog('POST_UserEatplePass')
    try:
        kakaoPayload = KakaoPayLoad(request)

        # User Validation
        user = userValidation(kakaoPayload)
        if (user == None):
            return GET_UserHome(request)

        return kakaoView_UseEatplePass(kakaoPayload)

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView('{}'.format(ex))


@csrf_exempt
def POST_OrderCancel(request):
    EatplusSkillLog('POST_OrderCancel')

    try:
        kakaoPayload = KakaoPayLoad(request)

        # User Validation
        user = userValidation(kakaoPayload)
        if (user == None):
            return GET_UserHome(request)

        return kakaoView_OrderCancel(kakaoPayload)

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView('{}'.format(ex))
