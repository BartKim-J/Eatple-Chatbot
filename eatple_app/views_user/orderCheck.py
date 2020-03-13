# View-System
from eatple_app.views_system.include import *
from eatple_app.views_system.debugger import *

# STATIC EP_define
ORDER_LIST_LENGTH = 4

# # # # # # # # # # # # # # # # # # # # # # # # #
#
# Static View
#
# # # # # # # # # # # # # # # # # # # # # # # # #


def eatplePassImg(order, delegatedEatplePassCount):
    imgUrl = ''

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

    return imgUrl


def eatplePass(order, ownEatplePass, delegatedEatplePassCount, delegatedEatplePass, nicknameList, ORDER_LIST_QUICKREPLIES_MAP, kakaoForm):
    isCafe = order.store.category.filter(name="카페").exists()
    if(isCafe):
        pickupTimeStr = dateByTimeZone(order.pickup_time).strftime(
            '%-m월 %-d일 오전 11시 30분 ~ 오후 4시')
    else:
        pickupTimeStr = dateByTimeZone(order.pickup_time).strftime(
            '%-m월 %-d일 %p %-I시 %-M분').replace('AM', '오전').replace('PM', '오후')

    thumbnail = {
        'imageUrl': eatplePassImg(order, delegatedEatplePassCount),
    }

    buttons = [
        {
            'action': 'block',
            'label': '사용하기(사장님 전용)',
            'messageText': KAKAO_EMOJI_LOADING,
            'blockId': KAKAO_BLOCK_USER_GET_USE_EATPLE_PASS_CONFIRM,
            'extra': {
                KAKAO_PARAM_ORDER_ID: order.order_id,
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_EATPLE_PASS
            }
        },
    ]

    if(delegatedEatplePass.count() > 0):
        # CAN EDIT COUPONS
        if (order.status == ORDER_STATUS_ORDER_CONFIRM_WAIT or
                order.status == ORDER_STATUS_ORDER_CONFIRMED):
            if(order.status == ORDER_STATUS_PICKUP_PREPARE):
                buttons.append(
                    {
                        'action': 'block',
                        'label': '부탁하기 전체취소',
                        'messageText': KAKAO_EMOJI_LOADING,
                        'blockId': KAKAO_BLOCK_USER_ORDER_SHARING_CANCEL_ALL,
                        'extra': {
                            KAKAO_PARAM_ORDER_ID: order.order_id,
                            KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_EATPLE_PASS
                        }
                    }
                )
            buttons.append(
                {
                    'action': 'block',
                    'label': '주문취소',
                    'messageText': KAKAO_EMOJI_LOADING,
                    'blockId': KAKAO_BLOCK_USER_POST_ORDER_CANCEL,
                    'extra': {
                        KAKAO_PARAM_ORDER_ID: order.order_id,
                        KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_EATPLE_PASS
                    }
                }
            )

        menuList = Menu.objects.filter(
            Q(store=order.store) &
            Q(status=OC_OPEN)
        )

        orderMenuStatus = []
        menuNameList = ''

        for menu in menuList:
            orderMenuStatus.append(dict({
                'name': menu.name,
                'count': delegatedEatplePass.filter(Q(menu=menu)).count() + ownEatplePass.filter(Q(menu=menu)).count()
            }))

        for status in orderMenuStatus:
            if(status['count'] > 0):
                menuNameList += ' - {} {}개\n'.format(
                    status['name'], status['count'])
            else:
                pass

        kakaoForm.BasicCard_Push(
            '총 잇플패스 : {}개'.format(
                delegatedEatplePass.count() + ownEatplePass.count()),
            '주문번호: {}\n - 주문자: {}\n\n메뉴 내역\n{}\n - 주문 상태: {}\n\n - 픽업 시간: {}'.format(
                order.order_id,
                nicknameList,
                menuNameList,
                order.store.addr,
                pickupTimeStr,
                dict(ORDER_STATUS)[order.status]
            ),
            thumbnail,
            buttons
        )

    else:
        if (order.status == ORDER_STATUS_ORDER_CONFIRM_WAIT or
            order.status == ORDER_STATUS_ORDER_CONFIRMED or
                order.status == ORDER_STATUS_PICKUP_PREPARE):
            buttons.append(
                {
                    'action': 'block',
                    'label': '픽업 부탁하기',
                    'messageText': KAKAO_EMOJI_LOADING,
                    'blockId': KAKAO_BLOCK_USER_ORDER_SHARING_START,
                    'extra': {
                        KAKAO_PARAM_ORDER_ID: order.order_id,
                        KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_EATPLE_PASS
                    }
                }
            )

        if(order.status == ORDER_STATUS_ORDER_CONFIRM_WAIT or
                order.status == ORDER_STATUS_ORDER_CONFIRMED):
            buttons.append(
                {
                    'action': 'block',
                    'label': '주문취소',
                    'messageText': KAKAO_EMOJI_LOADING,
                    'blockId': KAKAO_BLOCK_USER_POST_ORDER_CANCEL,
                    'extra': {
                        KAKAO_PARAM_ORDER_ID: order.order_id,
                        KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_EATPLE_PASS
                    }
                }
            )
            if(isCafe == False):
                pickupTimes = order.menu.pickup_time.filter(
                    selling_time=order.menu.selling_time)

                if(pickupTimes.count() > 1):
                    ORDER_LIST_QUICKREPLIES_MAP.append(
                        {
                            'action': 'block',
                            'label': '픽업 시간 변경',
                            'messageText': KAKAO_EMOJI_LOADING,
                            'blockId': KAKAO_BLOCK_USER_EDIT_PICKUP_TIME,
                            'extra': {
                                KAKAO_PARAM_ORDER_ID: order.order_id,
                                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_EATPLE_PASS
                            }
                        }
                    )

        kakaoForm.BasicCard_Push(
            '{}'.format(order.menu.name),
            '주문번호: {}\n - 주문자: {}({})\n\n - 매장: {}\n - 주문 상태: {}\n\n - 픽업 시간: {}'.format(
                order.order_id,
                order.ordersheet.user.nickname,
                str(order.ordersheet.user.phone_number)[9:13],
                order.store.name,
                dict(ORDER_STATUS)[order.status],
                pickupTimeStr,
            ),
            thumbnail,
            buttons
        )


def eatplePassDelegated(order, ownEatplePass, delegatedEatplePassCount, delegatedEatplePass, nicknameList, ORDER_LIST_QUICKREPLIES_MAP, kakaoForm):
    isCafe = order.store.category.filter(name="카페").exists()
    if(isCafe):
        pickupTimeStr = dateByTimeZone(order.pickup_time).strftime(
            '%-m월 %-d일 오전 11시 30분 ~ 오후 4시')
    else:
        pickupTimeStr = dateByTimeZone(order.pickup_time).strftime(
            '%-m월 %-d일 %p %-I시 %-M분').replace('AM', '오전').replace('PM', '오후')

    thumbnail = {
        'imageUrl': eatplePassImg(order, delegatedEatplePassCount),
    }

    buttons = []

    # CAN EDIT COUPONS
    if (order.status == ORDER_STATUS_ORDER_CONFIRM_WAIT or
            order.status == ORDER_STATUS_ORDER_CONFIRMED):
        if(order.status == ORDER_STATUS_PICKUP_PREPARE):
            buttons.append(
                {
                    'action': 'block',
                    'label': '부탁하기 취소',
                    'messageText': KAKAO_EMOJI_LOADING,
                    'blockId': KAKAO_BLOCK_USER_ORDER_SHARING_CANCEL,
                    'extra': {
                        KAKAO_PARAM_ORDER_ID: order.order_id,
                        KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_EATPLE_PASS
                    }
                }
            )
        buttons.append(
            {
                'action': 'block',
                'label': '주문취소',
                'messageText': KAKAO_EMOJI_LOADING,
                'blockId': KAKAO_BLOCK_USER_POST_ORDER_CANCEL,
                'extra': {
                    KAKAO_PARAM_ORDER_ID: order.order_id,
                    KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_EATPLE_PASS
                }
            }
        )

    kakaoForm.BasicCard_Push(
        '{}님에게 부탁된 잇플패스 입니다.'.format(order.delegate.nickname),
        '주문번호: {}\n - 소유자: {}({})\n\n - 위임자: {}({})\n\n - 매장: {}\n - 주문 상태: {}\n\n - 픽업 시간: {}'.format(
            order.order_id,
            order.ordersheet.user.nickname,
            str(order.ordersheet.user.phone_number)[9:13],
            order.delegate.nickname,
            str(order.delegate.phone_number)[9:13],
            order.store.name,
            dict(ORDER_STATUS)[order.status],
            pickupTimeStr,
        ),
        thumbnail,
        buttons
    )


def kakaoView_EatplePass(kakaoPayload):
    kakaoForm = KakaoForm()

    ORDER_LIST_QUICKREPLIES_MAP = [
        {
            'action': 'block',
            'label': '새로고침',
            'messageText': KAKAO_EMOJI_LOADING,
            'blockId': KAKAO_BLOCK_USER_EATPLE_PASS,
            'extra': {}
        },
        {
            'action': 'block',
            'label': '🏠  홈',
            'messageText': KAKAO_EMOJI_LOADING,
            'blockId': KAKAO_BLOCK_USER_HOME,
            'extra': {}
        },
    ]

    # User Validation
    user = userValidation(kakaoPayload)
    if (user == None):
        return errorView('잘못된 블럭 경로', '정상적이지 않은 경로거나, 잘못된 계정입니다.')

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
            nicknameList += ', {nickname}'.format(
                nickname=order.ordersheet.user.nickname)

    # Listup EatplePass
    if ownEatplePass:
        for order in ownEatplePass:
            if(order.delegate == None):
                eatplePass(
                    order,
                    ownEatplePass,
                    delegatedEatplePassCount,
                    delegatedEatplePass,
                    nicknameList,
                    ORDER_LIST_QUICKREPLIES_MAP,
                    kakaoForm
                )
            else:
                eatplePassDelegated(
                    order,
                    ownEatplePass,
                    delegatedEatplePassCount,
                    delegatedEatplePass,
                    nicknameList,
                    ORDER_LIST_QUICKREPLIES_MAP,
                    kakaoForm
                )

        kakaoForm.BasicCard_Add()

        if(order.delegate == None):

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

            buttons = [
                {
                    'action': 'osLink',
                    'label': '길찾기',
                    'osLink': {
                        'android': kakaoMapUrlAndriod,
                        'ios': kakaoMapUrlIOS,
                        'pc': kakaoMapUrl,
                    }
                }
            ]

            KakaoInstantForm().Message(
                '{}'.format(order.store.addr),
                buttons=buttons,
                kakaoForm=kakaoForm
            )

    # No EatplePass
    else:
        KakaoInstantForm().Message(
            '현재 조회 가능한 잇플패스가 없습니다.',
            '주문이 처음이시라면 사용 매뉴얼을 읽어주세요!',
            kakaoForm=kakaoForm
        )

    kakaoForm.QuickReplies_AddWithMap(ORDER_LIST_QUICKREPLIES_MAP)

    return JsonResponse(kakaoForm.GetForm())


def kakaoView_OrderDetails(kakaoPayload):
    kakaoForm = KakaoForm()

    ORDER_LIST_QUICKREPLIES_MAP = [
        {
            'action': 'block',
            'label': '🏠  홈',
            'messageText': KAKAO_EMOJI_LOADING,
            'blockId': KAKAO_BLOCK_USER_HOME,
            'extra': {}
        },
    ]

    # Block Validation
    prev_block_id = prevBlockValidation(kakaoPayload)
    if(prev_block_id != KAKAO_BLOCK_USER_HOME and prev_block_id != KAKAO_BLOCK_USER_ORDER_DETAILS):
        return errorView('Invalid Block ID', '정상적이지 않은 경로거나, 오류가 발생했습니다.\n다시 주문해주세요!')

    # User Validation
    user = userValidation(kakaoPayload)
    if (user == None):
        return errorView('잘못된 블럭 경로', '정상적이지 않은 경로거나, 잘못된 계정입니다.')

    orderManager = UserOrderManager(user)
    orderManager.orderPaidCheck()
    orderManager.orderPenddingCleanUp()

    unavailableOrders = orderManager.getUnavailableOrders().filter(
        Q(ordersheet__user=user))[:ORDER_LIST_LENGTH]

    if unavailableOrders:
        for order in unavailableOrders:
            KakaoInstantForm().OrderList(
                order,
                kakaoForm
            )

        kakaoForm.BasicCard_Add()
    else:
        KakaoInstantForm().Message(
            '이런.. 주문 내역이 없군요.',
            '주문이 처음이시라면 사용 매뉴얼을 읽어주세요!',
            kakaoForm=kakaoForm
        )

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
