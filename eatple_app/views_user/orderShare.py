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

import phonenumbers

# # # # # # # # # # # # # # # # # # # # # # # # #
#
# Static Return
#
# # # # # # # # # # # # # # # # # # # # # # # # #


def getDelegateUser(phone_number):
    try:
        user = User.objects.get(phone_number=phone_number)
        return user
    except (User.DoesNotExist, ValueError):
        return None


# # # # # # # # # # # # # # # # # # # # # # # # #
#
# Static View
#
# # # # # # # # # # # # # # # # # # # # # # # # #

def kakaoView_GetDelegateUser(kakaoPayload):
    kakaoForm = KakaoForm()

    QUICKREPLIES_MAP = [
        {
            'action': 'block',
            'label': '홈으로 돌아가기',
            'messageText': KAKAO_EMOJI_LOADING,
            'blockId': KAKAO_BLOCK_USER_HOME,
            'extra': {}
        },
    ]

    # Block Validation
    prev_block_id = prevBlockValidation(kakaoPayload)
    if(prev_block_id != KAKAO_BLOCK_USER_EATPLE_PASS and prev_block_id != KAKAO_BLOCK_USER_ORDER_SHARING_START):
        return errorView('Invalid Block ID', '정상적이지 않은 경로로 블럭에 들어왔습니다.\n주문을 다시 해주세요!')

    # User Validation
    user = userValidation(kakaoPayload)
    if (user == None):
        return errorView('잘못된 블럭 경로', '정상적이지 않은 경로거나, 잘못된 계정입니다.')

    order = orderValidation(kakaoPayload)
    if(order == None):
        return errorView('잘못된 블럭 경로', '정상적이지 않은 경로거나, 잘못된 주문번호입니다.\n홈으로 돌아가 다시 주문해주세요!')
    else:
        order.orderStatusUpdate()

    kakaoParam_phone_number = kakaoPayload.dataActionParams['phone_number']['origin']

    if(order.status == ORDER_STATUS_ORDER_CANCELED):
        KakaoInstantForm().Message(
            ' - 주의! -',
            '이미 취소된 잇플패스입니다. 다시 주문을 정확히 확인해주세요.',
            kakaoForm=kakaoForm
        )

        kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)
        return JsonResponse(kakaoForm.GetForm())

    elif(order.status == ORDER_STATUS_PICKUP_COMPLETED):
        KakaoInstantForm().Message(
            ' - 주의! -',
            '이미 사용된 잇플패스입니다. 다시 주문을 정확히 확인해주세요.',
            kakaoForm=kakaoForm
        )

        kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)
        return JsonResponse(kakaoForm.GetForm())

    elif(order.status == ORDER_STATUS_ORDER_FAILED):
        KakaoInstantForm().Message(
            ' - 주의! -',
            '결제 실패한 잇플패스입니다. 다시 주문을 확인해주세요',
            kakaoForm=kakaoForm
        )
        kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)
        return JsonResponse(kakaoForm.GetForm())

    try:
        phone_number = phonenumbers.format_number(
            phonenumbers.parse(
                "+82 {}".format(kakaoParam_phone_number
                                ), None),
            phonenumbers.PhoneNumberFormat.E164
        )
    except phonenumbers.phonenumberutil.NumberParseException:
        buttons = [
            {
                'action': 'block',
                'label': '전화번호 다시 입력',
                'messageText': KAKAO_EMOJI_LOADING,
                'blockId': KAKAO_BLOCK_USER_ORDER_SHARING_START,
                'extra': {
                    KAKAO_PARAM_ORDER_ID: order.order_id,
                    KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_ORDER_SHARING_START
                }
            },
        ]

        KakaoInstantForm().Message(
            '부탁하기에 실패했습니다.',
            '알수없는 번호거나 잘못된 입력입니다.\n - 입력된 전화번호: {}'.format(
                kakaoParam_phone_number),
            buttons=buttons,
            kakaoForm=kakaoForm
        )

        kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)

        return JsonResponse(kakaoForm.GetForm())

    delegateUser = getDelegateUser(phone_number)

    orderManager = UserOrderManager(delegateUser)
    orderManager.orderPaidCheck()
    orderManager.orderPenddingCleanUp()

    delegateUserOrder = orderManager.availableOrderStatusUpdate().filter(
        Q(ordersheet__user=delegateUser)).first()
    delegateUserOrder.orderStatusUpdate()

    if (order.status != ORDER_STATUS_ORDER_CONFIRM_WAIT and
        order.status != ORDER_STATUS_ORDER_CONFIRMED and
            order.status != ORDER_STATUS_PICKUP_PREPARE):
        KakaoInstantForm().Message(
            '현재는 부탁하기가 불가능한 시간입니다.',
            '부탁 가능 시간 : 픽업 시간 15분 전까지',
            kakaoForm=kakaoForm
        )

        kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)

        return JsonResponse(kakaoForm.GetForm())

    if(delegateUser == user):
        buttons = [
            {
                'action': 'block',
                'label': '전화번호 다시 입력',
                'messageText': KAKAO_EMOJI_LOADING,
                'blockId': KAKAO_BLOCK_USER_ORDER_SHARING_START,
                'extra': {
                    KAKAO_PARAM_ORDER_ID: order.order_id,
                    KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_ORDER_SHARING_START
                }
            },
        ]
        KakaoInstantForm().Message(
            '자기 자신에게 부탁하기를 할 수 없습니다.',
            '정확한 전화번호를 입력해주세요!',
            buttons=buttons,
            kakaoForm=kakaoForm
        )
    elif(order.delegate != None):
        KakaoInstantForm().Message(
            '현재 부탁하기를 한 상태 입니다.',
            '다른 사람에게 부탁하려면 현재 부탁하기를 취소해주세요.',
            kakaoForm=kakaoForm
        )
    elif(delegateUserOrder.delegate != None):
        KakaoInstantForm().Message(
            '다른사람에게 부탁하기를 한 사람에게는 부탁 할 수 없습니다.',
            '상대방의 주문을 확인해주세요.',
            kakaoForm=kakaoForm
        )
    else:
        if(delegateUser != None):
            if(delegateUserOrder != None):
                order = order.orderDelegate(delegateUserOrder)

                if(order.delegate != None):
                    buttons = [
                        {
                            'action': 'block',
                            'label': '잇플패스 확인',
                            'messageText': KAKAO_EMOJI_LOADING,
                            'blockId': KAKAO_BLOCK_USER_EATPLE_PASS,
                            'extra': {}
                        },
                    ]
                    KakaoInstantForm().Message(
                        '부탁하기가 완료되었습니다.',
                        '위임된 유저: {}({})'.format(delegateUser.nickname, str(
                            delegateUser.phone_number.as_national)[9:13]),
                        buttons=buttons,
                        kakaoForm=kakaoForm
                    )
                else:
                    KakaoInstantForm().Message(
                        '부탁하기 유저와 주문이 달라요.',
                        '주문과 픽업시간이 부탁 할 유저와 동일해야합니다.',
                        kakaoForm=kakaoForm
                    )
            else:
                KakaoInstantForm().Message(
                    '부탁 할 유저가 아직 주문을 하지 않았어요!',
                    '부탁하기는 주문한 유저에게만 요청 할 수 있어요.',
                    kakaoForm=kakaoForm
                )
        else:
            buttons = [
                {
                    'action': 'block',
                    'label': '전화번호 다시 입력',
                    'messageText': KAKAO_EMOJI_LOADING,
                    'blockId': KAKAO_BLOCK_USER_ORDER_SHARING_START,
                    'extra': {
                        KAKAO_PARAM_ORDER_ID: order.order_id,
                        KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_ORDER_SHARING_START
                    }
                },
            ]
            KakaoInstantForm().Message(
                '부탁하기에 실패했습니다.',
                '알수없는 번호거나 잘못된 입력입니다.\n - 입력된 전화번호: {}'.format(
                    kakaoParam_phone_number),
                buttons=buttons,
                kakaoForm=kakaoForm
            )
    kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)

    return JsonResponse(kakaoForm.GetForm())


def kakaoView_DelegateUserRemove(kakaoPayload):
    kakaoForm = KakaoForm()

    QUICKREPLIES_MAP = [
        {
            'action': 'block',
            'label': '홈으로 돌아가기',
            'messageText': KAKAO_EMOJI_LOADING,
            'blockId': KAKAO_BLOCK_USER_HOME,
            'extra': {}
        },
    ]

    buttons = [
        {
            'action': 'block',
            'label': '잇플패스 확인',
            'messageText': KAKAO_EMOJI_LOADING,
            'blockId': KAKAO_BLOCK_USER_EATPLE_PASS,
            'extra': {}
        },
    ]

    # Block Validation
    prev_block_id = prevBlockValidation(kakaoPayload)
    if(prev_block_id != KAKAO_BLOCK_USER_EATPLE_PASS):
        return errorView('Invalid Block ID', '정상적이지 않은 경로로 블럭에 들어왔습니다.\n주문을 다시 해주세요!')

    # User Validation
    user = userValidation(kakaoPayload)
    if (user == None):
        return errorView('잘못된 블럭 경로', '정상적이지 않은 경로거나, 잘못된 계정입니다.')

    order = orderValidation(kakaoPayload)
    if(order == None):
        return errorView('잘못된 블럭 경로', '정상적이지 않은 경로거나, 잘못된 주문번호입니다.\n홈으로 돌아가 다시 주문해주세요!')
    else:
        order.orderStatusUpdate()

    isCafe = order.store.category.filter(name="카페").exists()

    if ((order.status != ORDER_STATUS_ORDER_CONFIRM_WAIT and
         order.status != ORDER_STATUS_ORDER_CONFIRMED and
            order.status != ORDER_STATUS_PICKUP_PREPARE) or isCafe):
        KakaoInstantForm().Message(
            '현재는 부탁하기 취소가 불가능한 시간입니다.',
            '부탁 가능 시간 : 픽업 시간 이전까지',
            kakaoForm=kakaoForm
        )

        kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)

        return JsonResponse(kakaoForm.GetForm())
    else:
        order.orderDelegateCancel()

    if(order.delegate == None):
        KakaoInstantForm().Message(
            '부탁하기를 취소 했습니다.',
            '주문 번호 : {}'.format(order.order_id),
            buttons=buttons,
            kakaoForm=kakaoForm
        )
    else:
        KakaoInstantForm().Message(
            '부탁하기를 취소하지 못했습니다.',
            '주문 번호 : {}'.format(order.order_id),
            buttons=buttons,
            kakaoForm=kakaoForm
        )

    kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)

    return JsonResponse(kakaoForm.GetForm())


def kakaoView_DelegateUserRemoveAll(kakaoPayload):
    kakaoForm = KakaoForm()

    buttons = [
        {
            'action': 'block',
            'label': '잇플패스 확인',
            'messageText': KAKAO_EMOJI_LOADING,
            'blockId': KAKAO_BLOCK_USER_EATPLE_PASS,
            'extra': {}
        },
    ]

    QUICKREPLIES_MAP = [
        {
            'action': 'block',
            'label': '홈으로 돌아가기',
            'messageText': KAKAO_EMOJI_LOADING,
            'blockId': KAKAO_BLOCK_USER_HOME,
            'extra': {}
        },
    ]

    # Block Validation
    prev_block_id = prevBlockValidation(kakaoPayload)
    if(prev_block_id != KAKAO_BLOCK_USER_EATPLE_PASS):
        return errorView('Invalid Block ID', '정상적이지 않은 경로로 블럭에 들어왔습니다.\n주문을 다시 해주세요!')

    # User Validation
    user = userValidation(kakaoPayload)
    if (user == None):
        return errorView('잘못된 블럭 경로', '정상적이지 않은 경로거나, 잘못된 계정입니다.')

    order = orderValidation(kakaoPayload)
    if(order == None):
        return errorView('잘못된 블럭 경로', '정상적이지 않은 경로거나, 잘못된 주문번호입니다.\n홈으로 돌아가 다시 주문해주세요!')
    else:
        order.orderStatusUpdate()

    orderManager = UserOrderManager(user)
    orderManager.orderPenddingCleanUp()

    availableEatplePass = orderManager.availableOrderStatusUpdate()
    ownEatplePass = availableEatplePass.filter(Q(delegate=None))
    delegatedEatplePass = availableEatplePass.filter(~Q(delegate=None))

    if (order.status != ORDER_STATUS_ORDER_CONFIRM_WAIT and
        order.status != ORDER_STATUS_ORDER_CONFIRMED and
            order.status != ORDER_STATUS_PICKUP_PREPARE):
        KakaoInstantForm().Message(
            '현재는 부탁하기 취소가 불가능한 시간입니다.',
            '부탁 가능 시간 : 픽업 시간 이전까지',
            buttons=buttons,
            kakaoForm=kakaoForm
        )

        kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)

        return JsonResponse(kakaoForm.GetForm())

    if delegatedEatplePass:
        for order in delegatedEatplePass:
            order.orderDelegateCancel()

        if(order.delegate != None):
            KakaoInstantForm().Message(
                '부탁하기를 취소하지 못했습니다.',
                '주문 번호 : {}'.format(order.order_id),
                buttons=buttons,
                kakaoForm=kakaoForm
            )

            kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)

            return JsonResponse(kakaoForm.GetForm())
    else:
        KakaoInstantForm().Message(
            '부탁하기를 취소하지 못했습니다.',
            '부탁을 받은 잇플패스가 없습니다.'.format(order.order_id),
            buttons=buttons,
            kakaoForm=kakaoForm
        )

    delegatedEatplePass = availableEatplePass.filter(~Q(delegate=None))

    if(delegatedEatplePass.count() == 0):
        KakaoInstantForm().Message(
            '받은 부탁하기를 전부 취소 했습니다.',
            '주문 번호 : {}'.format(order.order_id),
            buttons=buttons,
            kakaoForm=kakaoForm
        )
    else:
        KakaoInstantForm().Message(
            '부탁하기를 취소하지 못했습니다.',
            '주문 번호 : {}'.format(order.order_id),
            buttons=buttons,
            kakaoForm=kakaoForm
        )

    kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)

    return JsonResponse(kakaoForm.GetForm())


# # # # # # # # # # # # # # # # # # # # # # # # #
#
# External View
#
# # # # # # # # # # # # # # # # # # # # # # # # #

@csrf_exempt
def GET_DelegateUserRemove(request):
    EatplusSkillLog('GET_DelegateUserRemove')
    try:
        kakaoPayload = KakaoPayLoad(request)

        # User Validation
        user = userValidation(kakaoPayload)
        if (user == None):
            return GET_UserHome(request)

        return kakaoView_DelegateUserRemove(kakaoPayload)

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView('{} '.format(ex))


@csrf_exempt
def GET_DelegateUserRemoveAll(request):
    EatplusSkillLog('GET_DelegateUserRemoveAll')
    try:
        kakaoPayload = KakaoPayLoad(request)

        # User Validation
        user = userValidation(kakaoPayload)
        if (user == None):
            return GET_UserHome(request)

        return kakaoView_DelegateUserRemoveAll(kakaoPayload)

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView('{} '.format(ex))


@csrf_exempt
def GET_DelegateUser(request):
    EatplusSkillLog('GET_DelegateUser')
    try:
        kakaoPayload = KakaoPayLoad(request)

        # User Validation
        user = userValidation(kakaoPayload)
        if (user == None):
            return GET_UserHome(request)

        return kakaoView_GetDelegateUser(kakaoPayload)

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView('{} '.format(ex))
