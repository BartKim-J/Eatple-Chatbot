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
from eatple_app.module_kakao.kakaoPay import *
from eatple_app.module_kakao.form import *
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
    kakaoForm = KakaoForm()

    QUICKREPLIES_MAP = [
        {
            'action': 'block',
            'label': '홈으로 돌아가기',
            'messageText': KAKAO_EMOJI_LOADING,
            'blockId': KAKAO_BLOCK_USER_HOME,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_ORDER_DETAILS
            }
        },
    ]

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

    if(order.status == ORDER_STATUS_PICKUP_COMPLETED):
        KakaoInstantForm().Message(
            ' - 주의! -',
            '이미 사용된 잇플패스입니다. 다시 주문을 확인해주세요.',
            kakaoForm=kakaoForm
        )
    elif(order.status == ORDER_STATUS_ORDER_EXPIRED):
        KakaoInstantForm().Message(
            ' - 주의! -',
            '이미 만료된 잇플패스입니다. 다시 주문을 확인해주세요.',
            kakaoForm=kakaoForm
        )
    elif(order.status == ORDER_STATUS_ORDER_FAILED):
        KakaoInstantForm().Message(
            ' - 주의! -',
            '결제 실패한 잇플패스입니다. 다시 주문을 확인해주세요',
            kakaoForm=kakaoForm
        )
    elif(order.status == ORDER_STATUS_PICKUP_WAIT):
        order = order.orderUsed()

        if delegatedEatplePass:
            for delegatedOrder in delegatedEatplePass:
                delegatedOrder = delegatedOrder.orderUsed()

        KakaoInstantForm().Message(
            '잇플패스가 사용되었습니다.',
            '\n - 주문자: {}({})\n\n - 매장: {} \n - 메뉴: {}'.format(
                order.ordersheet.user.nickname,
                str(order.ordersheet.user.phone_number)[9:13],
                order.store.name,
                order.menu.name,
            ),
            kakaoForm=kakaoForm
        )
    else:
        KakaoInstantForm().Message(
            '사용 가능한 픽업 시간이 아닙니다!',
            '잇플패스의 픽업 시간을 확인해주세요!',
            kakaoForm=kakaoForm
        )

    kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)

    return JsonResponse(kakaoForm.GetForm())


def kakaoView_ConfirmUseEatplePass(kakaoPayload):
    kakaoForm = KakaoForm()

    QUICKREPLIES_MAP = [
        {
            'action': 'block',
            'label': '홈으로 돌아가기',
            'messageText': KAKAO_EMOJI_LOADING,
            'blockId': KAKAO_BLOCK_USER_HOME,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_GET_USE_EATPLE_PASS_CONFIRM
            }
        },
        {
            'action': 'block',
            'label': '새로고침',
            'messageText': KAKAO_EMOJI_LOADING,
            'blockId': KAKAO_BLOCK_USER_EATPLE_PASS,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_GET_USE_EATPLE_PASS_CONFIRM
            }
        },
    ]

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

    if(order.delegate != None):
        KakaoInstantForm().Message(
            '타인에게 부탁한 잇플패스는 사용이 불가능합니다.',
            '사용하시고 싶다면 \'부탁하기 취소\'를 한 다음 사용해주세요!',
            kakaoForm=kakaoForm
        )

        kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)
        return JsonResponse(kakaoForm.GetForm())

    elif(order.status == ORDER_STATUS_ORDER_CANCELED):
        KakaoInstantForm().Message(
            ' - 주의! -',
            '이미 취소된 잇플패스입니다. 다시 주문을 정확히 확인해주세요.',
            kakaoForm=kakaoForm
        )

    elif(order.status == ORDER_STATUS_PICKUP_COMPLETED):
        KakaoInstantForm().Message(
            ' - 주의! -',
            '이미 사용된 잇플패스입니다. 다시 주문을 정확히 확인해주세요.',
            kakaoForm=kakaoForm
        )

    elif(order.status == ORDER_STATUS_ORDER_FAILED):
        KakaoInstantForm().Message(
            ' - 주의! -',
            '결제 실패한 잇플패스입니다. 다시 주문을 확인해주세요',
            kakaoForm=kakaoForm
        )
    elif(order.status == ORDER_STATUS_PICKUP_WAIT):
        buttons = [
            {
                'action': 'block',
                'label': '확인',
                'messageText': KAKAO_EMOJI_LOADING,
                'blockId': KAKAO_BLOCK_USER_POST_USE_EATPLE_PASS,
                'extra': {
                    KAKAO_PARAM_ORDER_ID: order.order_id,
                    KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_GET_USE_EATPLE_PASS_CONFIRM
                }
            },
            {
                'action': 'block',
                'label': '돌아가기',
                'messageText': KAKAO_EMOJI_LOADING,
                'blockId': KAKAO_BLOCK_USER_EATPLE_PASS,
                'extra': {
                    KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_GET_USE_EATPLE_PASS_CONFIRM
                }
            },
        ]

        if delegatedEatplePass:
            KakaoInstantForm().Message(
                '총 {}개의 잇플패스를 사용하시겠습니까?'.format(
                    delegatedEatplePass.count() + ownEatplePass.count()),
                '부탁받은 잇플패스를 포함하여 전부 사용하게됩니다.',
                buttons=buttons,
                kakaoForm=kakaoForm
            )

        else:
            KakaoInstantForm().Message(
                '잇플패스를 사용하시겠습니까?',
                '사용한 이후에는 취소/환불이 불가능합니다.',
                buttons=buttons,
                kakaoForm=kakaoForm
            )
    else:
        KakaoInstantForm().Message(
            '사용 가능한 픽업 시간이 아닙니다!',
            '잇플패스의 픽업 시간을 확인해주세요!',
            kakaoForm=kakaoForm
        )

    kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)
    return JsonResponse(kakaoForm.GetForm())


def kakaoView_OrderCancel(kakaoPayload):
    kakaoForm = KakaoForm()

    QUICKREPLIES_MAP = [
        {
            'action': 'block',
            'label': '새로고침',
            'messageText': KAKAO_EMOJI_LOADING,
            'blockId': KAKAO_BLOCK_USER_EATPLE_PASS,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_EATPLE_PASS
            }
        },
        {
            'action': 'block',
            'label': '홈으로 돌아가기',
            'messageText': KAKAO_EMOJI_LOADING,
            'blockId': KAKAO_BLOCK_USER_HOME,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_EATPLE_PASS
            }
        },
    ]

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

    if(order.status == ORDER_STATUS_ORDER_CANCELED):
        KakaoInstantForm().Message(
            '이 잇플패스는 이미 취소된 잇플패스입니다.',
            '다시 주문을 확인해주세요.',
            kakaoForm=kakaoForm
        )

    elif (order.status == ORDER_STATUS_ORDER_CONFIRM_WAIT or
            order.status == ORDER_STATUS_ORDER_CONFIRMED):

        response = order.orderCancel()
        if(response == False):
            return errorView('Invalid Paratmer', '정상적이지 않은 주문번호이거나\n환불 진행 중 오류가 발생했습니다.')

        # Cancelled EatplePass Update
        order.orderDelegateCancel()
        order.orderStatusUpdate()

        kakaoMapUrl = 'https://map.kakao.com/link/map/{name},{place}'.format(
            name=order.store.name,
            place=order.store.place
        )

        kakaoMapUrlAndriod = 'http://m.map.kakao.com/scheme/route?ep={place}&by=FOOT'.format(
            place=order.store.place
        )

        kakaoMapUrlIOS = 'http://m.map.kakao.com/scheme/route?ep={place}&by=FOOT'.format(
            place=order.store.place
        )

        isCafe = order.store.category.filter(name="카페").exists()
        if(isCafe):
            pickupTimeStr = dateByTimeZone(order.pickup_time).strftime(
                '%-m월 %-d일 오전 11시 30분 ~ 오후 4시')
        else:
            pickupTimeStr = dateByTimeZone(order.pickup_time).strftime(
                '%-m월 %-d일 %p %-I시 %-M분').replace('AM', '오전').replace('PM', '오후')

        KakaoInstantForm().Message(
            '주문이 취소되었습니다.',
            '{}\n\n - 주문자: {}({})\n - 매장: {}\n\n - 픽업 시간: {}'.format(
                order.menu.name,
                order.ordersheet.user.nickname,
                str(order.ordersheet.user.phone_number)[9:13],
                order.store.name,
                pickupTimeStr,
            ),
            kakaoForm=kakaoForm
        )
    else:
        KakaoInstantForm().Message(
            '현재는 주문을 취소 할 수 없는 시간입니다.',
            '취소 가능 시간 : 픽업 당일 오전 10시 30분까지',
            kakaoForm=kakaoForm
        )

    kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)
    return JsonResponse(kakaoForm.GetForm())


def kakaoView_EditPickupTime(kakaoPayload):
    kakaoForm = KakaoForm()

    QUICKREPLIES_MAP = [
        {
            'action': 'block',
            'label': '홈으로 돌아가기',
            'messageText': KAKAO_EMOJI_LOADING,
            'blockId': KAKAO_BLOCK_USER_HOME,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_EDIT_PICKUP_TIME
            }
        },
    ]

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

    if(order.status == ORDER_STATUS_ORDER_CANCELED):
        KakaoInstantForm().Message(
            ' - 주의! -',
            '이 잇플패스는 이미 취소된 잇플패스입니다. 다시 주문을 정확히 확인해주세요.',
            kakaoForm=kakaoForm
        )
        kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)
    elif(order.status != ORDER_STATUS_ORDER_CONFIRM_WAIT and
            order.status != ORDER_STATUS_ORDER_CONFIRMED):
        KakaoInstantForm().Message(
            '현재는 픽업시간을 변경 할 수 없는 시간입니다.',
            '변경 가능 시간 : 픽업 당일 오전 10시 30분까지',
            kakaoForm=kakaoForm
        )
        kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)
    else:
        KakaoInstantForm().Message(
            '변경할 픽업시간을 선택해주세요.',
            ' - 현재 픽업시간 : {}'.format(
                dateByTimeZone(order.pickup_time).strftime('%p %-I시 %-M분').replace('AM', '오전').replace('PM', '오후'),),
            kakaoForm=kakaoForm
        )

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
                    KAKAO_EMOJI_LOADING,
                    KAKAO_BLOCK_USER_EDIT_PICKUP_TIME_CONFIRM,
                    dataActionExtra
                )

        kakaoForm.QuickReplies_Add(
            'block',
            '돌아가기',
            KAKAO_EMOJI_LOADING,
            KAKAO_BLOCK_USER_EATPLE_PASS,
            {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_EDIT_PICKUP_TIME_CONFIRM
            }
        )

    return JsonResponse(kakaoForm.GetForm())


def kakaoView_ConfirmEditPickupTime(kakaoPayload):
    kakaoForm = KakaoForm()

    QUICKREPLIES_MAP = [
        {
            'action': 'block',
            'label': '홈으로 돌아가기',
            'messageText': KAKAO_EMOJI_LOADING,
            'blockId': KAKAO_BLOCK_USER_HOME,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_EDIT_PICKUP_TIME
            }
        },
    ]

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

    if(order.status == ORDER_STATUS_ORDER_CANCELED):
        KakaoInstantForm().Message(
            '이 잇플패스는 이미 취소된 잇플패스입니다.',
            '다시 주문을 확인해주세요.',
            kakaoForm=kakaoForm
        )
        kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)
    elif (order.status != ORDER_STATUS_ORDER_CONFIRM_WAIT and
            order.status != ORDER_STATUS_ORDER_CONFIRMED):
        KakaoInstantForm().Message(
            '현재는 픽업시간을 변경 할 수 없는 시간입니다.',
            '변경 가능 시간 : 픽업 당일 오전 10시 30분까지',
            kakaoForm=kakaoForm
        )
        kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)
    else:
        KakaoInstantForm().Message(
            '픽업타임이 변경되었습니다.',
            '{}  ➔  {}'.format(
                beforePickupTime.strftime(
                    '%p %-I시 %-M분').replace('AM', '오전').replace('PM', '오후'),
                order.pickup_time.strftime(
                    '%p %-I시 %-M분').replace('AM', '오전').replace('PM', '오후'),
            ),
            kakaoForm=kakaoForm
        )

        kakaoForm.QuickReplies_Add(
            'block',
            '돌아가기',
            KAKAO_EMOJI_LOADING,
            KAKAO_BLOCK_USER_EATPLE_PASS,
            {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_EDIT_PICKUP_TIME_CONFIRM
            }
        )

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
        return errorView('{} '.format(ex))

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
        return errorView('{} '.format(ex))


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
