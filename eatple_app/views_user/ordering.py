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
MENU_LIST_LENGTH = 20

# # # # # # # # # # # # # # # # # # # # # # # # #
#
# Static View
#
# # # # # # # # # # # # # # # # # # # # # # # # #


def kakaoView_MenuListup(kakaoPayload):
    # Block Validation
    prev_block_id = prevBlockValidation(kakaoPayload)
    if(prev_block_id != KAKAO_BLOCK_USER_HOME and
       prev_block_id != KAKAO_BLOCK_USER_EATPLE_PASS and
       prev_block_id != KAKAO_BLOCK_USER_ORDER_DETAILS and
       prev_block_id != KAKAO_BLOCK_USER_SET_PICKUP_TIME):
        return errorView('잘못된 블럭 경로', '정상적이지 않은 경로거나 오류가 발생했습니다.')

    # User Validation
    user = userValidation(kakaoPayload)
    if (user == None):
        return errorView('잘못된 사용자 계정', '찾을 수 없는 사용자 계정 아이디입니다.')

    # Order Log Record
    orderRecordSheet = OrderRecordSheet()
    orderRecordSheet.user = user
    orderRecordSheet.recordUpdate(ORDER_RECORD_GET_MENU)

    order = orderValidation(kakaoPayload)
    if(order == None):
        orderSheet = OrderSheet()
        order = orderSheet.pushOrder(
            user=user,
            menu=None,
            store=None,
            pickup_time='00:00',
            totalPrice=0,
            count=1,
            type=ORDER_TYPE_NORMAL
        )

        if(isB2BUser(user)):
            order.type = ORDER_TYPE_B2B
        else:
            order.type = ORDER_TYPE_NORMAL

        order.save()
    else:
        order.pickup_time = order.pickupTimeToDateTime(pickup_time)
        order.totalPrice = menu.price
        order.save()

    # @PROMOTION
    # currentSellingTime = sellingTimeCheck()
    currentSellingTime = SELLING_TIME_LUNCH

    if(isB2BUser(user)):
        storeFilterType = STORE_TYPE_B2B
    else:
        storeFilterType = STORE_TYPE_NORMAL

    menuList = Menu.objects.annotate(
        distance=Distance(F('store__place__point'),
                          user.location.point) * 100 * 1000
    ).filter(
        Q(selling_time=currentSellingTime) &
        Q(store__type=storeFilterType) &

        Q(status=OC_OPEN) &
        Q(store__status=OC_OPEN) |
        Q(store__status=STORE_OC_VACATION),
    ).order_by(F'distance')

    sellingOutList = []

    if menuList:
        kakaoForm = KakaoForm()

        if(isB2BUser(user)):
            kakaoForm.BasicCard_Push('※ 하단 메뉴 중 픽업 하실 메뉴를 선택해주세요.',
                                     '',
                                     {},
                                     []
                                     )
        else:
            kakaoForm.BasicCard_Push('※ 잇플의 모든 메뉴는 6000원입니다.',
                                     '',
                                     {},
                                     []
                                     )

        kakaoForm.BasicCard_Add()

        # Menu Carousel Card Add
        for menu in menuList:
            distance = menu.distance
            walkTime = round((distance / 100) * 2.1)

            if(distance <= 1000):
                walkTime = '약 도보 {} 분'.format(walkTime)
            else:
                walkTime = '1 ㎞ 이상'

            thumbnail = {
                'imageUrl': '{}{}'.format(HOST_URL, menu.imgURL()),
                'fixedRatio': 'true',
                'width': 800,
                'height': 800,
            }

            kakaoMapUrl = 'https://map.kakao.com/link/map/{},{}'.format(
                menu.store.name, menu.store.place)

            currentStock = menu.getCurrentStock()

            if(menu.max_stock > menu.current_stock and menu.store.status == STORE_OC_OPEN):
                buttons = [
                    {
                        'action': 'block',
                        'label': '주문하기',
                        'messageText': '로딩중..',
                        'blockId': KAKAO_BLOCK_USER_SET_PICKUP_TIME,
                        'extra': {
                            KAKAO_PARAM_STORE_ID: menu.store.store_id,
                            KAKAO_PARAM_MENU_ID: menu.menu_id,
                            KAKAO_PARAM_ORDER_ID: order.order_id,
                            KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_GET_MENU
                        }
                    },
                    {
                        'action': 'webLink',
                        'label': '위치보기',
                        'webLinkUrl': kakaoMapUrl
                    },
                ]

                kakaoForm.BasicCard_Push(
                    '{} - {}'.format(
                        menu.store.name,
                        walkTime,
                    ),
                    '{}'.format(
                        menu.description,
                    ),
                    thumbnail,
                    buttons
                )

            else:  # selling out
                sellingOutList.extend(list(Menu.objects.filter(id=menu.id)))

        for menu in sellingOutList:
            if(menu.store.status == STORE_OC_VACATION):
                thumbnail = {
                    'imageUrl': '{}{}'.format(HOST_URL, menu.imgURL()),
                    'fixedRatio': 'true',
                    'width': 800,
                    'height': 800,
                }
                buttons = [
                    {
                        'action': 'webLink',
                        'label': '위치보기',
                        'webLinkUrl': kakaoMapUrl
                    },
                ]

                kakaoForm.BasicCard_Push(
                    '{} - {}'.format(
                        menu.store.name,
                        "휴무 중",
                    ),
                    '{}'.format(
                        menu.description,
                    ),
                    thumbnail,
                    buttons
                )
            else:
                thumbnail = {
                    'imageUrl': '{}{}'.format(HOST_URL, menu.soldOutImgURL()),
                    'fixedRatio': 'true',
                    'width': 800,
                    'height': 800,
                }

                buttons = [
                    {
                        'action': 'webLink',
                        'label': '위치보기',
                        'webLinkUrl': kakaoMapUrl
                    },
                ]

                kakaoForm.BasicCard_Push(
                    '{} - {}'.format(
                        menu.store.name,
                        walkTime,
                    ),
                    '{}'.format(
                        menu.description,
                    ),
                    thumbnail,
                    buttons
                )
        kakaoForm.BasicCard_Add()

    else:
        kakaoForm = KakaoForm()

        kakaoForm.SimpleText_Add('판매중인 메뉴가 없어요...')

    QUICKREPLIES_MAP = [
        {
            'action': 'block',
            'label': '홈으로 돌아가기',
            'messageText': '로딩중..',
            'blockId': KAKAO_BLOCK_USER_HOME,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_GET_MENU
            }
        },
    ]

    kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)

    return JsonResponse(kakaoForm.GetForm())


def kakaoView_PickupTime(kakaoPayload):
    # Block Validation
    prev_block_id = prevBlockValidation(kakaoPayload)
    if(prev_block_id != KAKAO_BLOCK_USER_GET_MENU and
            prev_block_id != KAKAO_BLOCK_USER_SET_ORDER_SHEET):
        return errorView('잘못된 블럭 경로', '정상적이지 않은 경로거나, 오류가 발생했습니다.\n다시 주문해주세요!')

    # User Validation
    user = userValidation(kakaoPayload)
    if (user == None):
        return errorView('잘못된 블럭 경로', '정상적이지 않은 경로거나, 잘못된 계정입니다.')

    # User's Eatple Pass Validation
    eatplePassStatus = eatplePassValidation(user)
    if(eatplePassStatus != None):
        return eatplePassStatus

    order = orderValidation(kakaoPayload)
    if(order == None):
        return errorView('잘못된 블럭 경로', '정상적이지 않은 경로거나, 오류가 발생했습니다.\n홈으로 돌아가 다시 주문해주세요!')

    store = storeValidation(kakaoPayload)
    menu = menuValidation(kakaoPayload)

    if(store == None or menu == None):
        return errorView('잘못된 블럭 경로', '정상적이지 않은 경로거나, 오류가 발생했습니다.\n다시 주문해주세요!')

    kakaoForm = KakaoForm()

    QUICKREPLIES_MAP = [
        {
            'action': 'block',
            'label': '홈으로 돌아가기',
            'messageText': '로딩중..',
            'blockId': KAKAO_BLOCK_USER_HOME,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_GET_MENU
            }
        },
    ]

    currentStock = menu.getCurrentStock()

    if(menu.max_stock <= menu.current_stock):
        kakaoForm.BasicCard_Push(
            '이 메뉴는 이미 매진됬습니다.',
            '아쉽지만 다른 메뉴를 주문해주세요!',
            {},
            []
        )
        kakaoForm.BasicCard_Add()

        kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)

        return JsonResponse(kakaoForm.GetForm())

    currentSellingTime = sellingTimeCheck()

    if (currentSellingTime == None):
        return errorView('Get Invalid Selling Time', '잘못된 주문 시간입니다.')
    elif currentSellingTime == SELLING_TIME_DINNER:
        '''
            @NOTE Dinner Time Close In Alpha 
        '''
        kakaoForm.BasicCard_Push(
            '오늘 점심은 이미 마감되었어요.',
            '내일 점심은 오늘 16:30부터 내일 10:30까지 주문하실 수 있어요.',
            {},
            []
        )
        kakaoForm.BasicCard_Add()

        kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)

        return JsonResponse(kakaoForm.GetForm())

    isVacationDay = vacationTimeCheck()
    isClosedDay = weekendTimeCheck()

    if(isClosedDay or isVacationDay):
        kakaoForm.BasicCard_Push('※ 안내사항 ※',
                                 '잇플은 \'주말 및 공휴일\'에 서비스 하지 않고있습니다.',
                                 {},
                                 []
                                 )

        kakaoForm.BasicCard_Add()

        kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)

        return JsonResponse(kakaoForm.GetForm())

    # Order Record
    try:
        orderRecordSheet = OrderRecordSheet.objects.latest('update_date')
    except OrderRecordSheet.DoesNotExist:
        orderRecordSheet = OrderRecordSheet()

    if (orderRecordSheet.timeoutValidation()):
        return kakaoView_TimeOut(KAKAO_BLOCK_USER_SET_PICKUP_TIME)

    orderRecordSheet.user = user
    orderRecordSheet.menu = menu
    orderRecordSheet.recordUpdate(ORDER_RECORD_SET_PICKUP_TIEM)

    PICKUP_TIME_QUICKREPLIES_MAP = []

    pickupTimes = menu.pickup_time.filter(selling_time=currentSellingTime)

    order = orderValidation(kakaoPayload)

    isCafe = store.category.filter(name="카페").exists()
    if(isCafe):
        kakaoForm.BasicCard_Push(
            '- 상시픽업이 가능한 점포입니다 -'.format(
                store.name),
            '오전 11:30 부터 오후 4:00까지 언제든 방문하여 메뉴를 픽업할 수 있습니다.',
            {},
            []
        )
        kakaoForm.BasicCard_Add()
    elif(pickupTimes.count() < 2):
        kakaoForm.BasicCard_Push(
            ' - 픽업시간이 제한된 점포입니다 -',
            '점주님의 요청으로 픽업시간이 한 타임으로 제한된 점포입니다.',
            {},
            []
        )
        kakaoForm.BasicCard_Add()

    kakaoForm.BasicCard_Push('픽업시간을 설정해주세요.',
                             '{} - {}'.format(menu.store.name, menu.name),
                             {},
                             []
                             )

    kakaoForm.BasicCard_Add()

    orderTimeTable = OrderTimeSheet()

    if(isCafe):
        dataActionExtra = {
            KAKAO_PARAM_STORE_ID: menu.store.store_id,
            KAKAO_PARAM_MENU_ID: menu.menu_id,
            KAKAO_PARAM_ORDER_ID: order.order_id,
            KAKAO_PARAM_PICKUP_TIME: orderTimeTable.GetLunchOrderPickupTimeStart().strftime('%H:%M'),
            KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_SET_PICKUP_TIME
        }

        kakaoForm.QuickReplies_Add(
            'block',
            "오전 11시 30분 ~ 오후 4시",
            '로딩중..',
            KAKAO_BLOCK_USER_SET_ORDER_SHEET,
            dataActionExtra
        )
    else:
        for pickupTime in pickupTimes:
            dataActionExtra = {
                KAKAO_PARAM_STORE_ID: menu.store.store_id,
                KAKAO_PARAM_MENU_ID: menu.menu_id,
                KAKAO_PARAM_ORDER_ID: order.order_id,
                KAKAO_PARAM_PICKUP_TIME: pickupTime.time.strftime('%H:%M'),
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_SET_PICKUP_TIME
            }

            if(order != None):
                dataActionExtra[KAKAO_PARAM_ORDER_ID] = order.order_id

            kakaoForm.QuickReplies_Add(
                'block',
                "{}".format(pickupTime.time.strftime(
                    '%p %-I시 %-M분').replace('AM', '오전').replace('PM', '오후')),
                '로딩중..',
                KAKAO_BLOCK_USER_SET_ORDER_SHEET,
                dataActionExtra
            )

    return JsonResponse(kakaoForm.GetForm())


def kakaoView_OrderPayment(kakaoPayload):
    # Block Validation
    prev_block_id = prevBlockValidation(kakaoPayload)
    if(prev_block_id != KAKAO_BLOCK_USER_SET_PICKUP_TIME and prev_block_id != KAKAO_BLOCK_USER_SET_ORDER_SHEET):
        return errorView('잘못된 블럭 경로', '정상적이지 않은 경로거나, 오류가 발생했습니다.\n다시 주문해주세요!')

    # User Validation
    user = userValidation(kakaoPayload)
    if (user == None):
        return errorView('잘못된 블럭 경로', '정상적이지 않은 경로거나, 잘못된 계정입니다.')

    # User's Eatple Pass Validation
    eatplePassStatus = eatplePassValidation(user)
    if(eatplePassStatus != None):
        return eatplePassStatus

    store = storeValidation(kakaoPayload)
    menu = menuValidation(kakaoPayload)
    pickup_time = pickupTimeValidation(kakaoPayload)

    if(store == None or menu == None or pickup_time == None):
        return errorView('잘못된 블럭 경로', '정상적이지 않은 경로거나, 오류가 발생했습니다.\n다시 주문해주세요!')

    order = orderValidation(kakaoPayload)
    if(order == None):
        return errorView('잘못된 블럭 경로', '정상적이지 않은 경로거나, 오류가 발생했습니다.\n다시 주문해주세요!')
    else:
        order.user = user
        order.menu = menu
        order.store = store
        order.pickup_time = order.pickupTimeToDateTime(pickup_time)
        order.totalPrice = menu.price
        order.count = 1
        order.save()

        if(isB2BUser(user)):
            order.type = ORDER_TYPE_B2B
        else:
            order.type = ORDER_TYPE_NORMAL

    # Order Record
    try:
        orderRecordSheet = OrderRecordSheet.objects.latest('update_date')
    except OrderRecordSheet.DoesNotExist:
        orderRecordSheet = OrderRecordSheet()

    if (orderRecordSheet.timeoutValidation()):
        return kakaoView_TimeOut(KAKAO_BLOCK_USER_SET_ORDER_SHEET)

    orderRecordSheet.user = user
    orderRecordSheet.menu = menu
    orderRecordSheet.recordUpdate(ORDER_RECORD_ORDERSHEET_CHECK)

    dataActionExtra = kakaoPayload.dataActionExtra
    dataActionExtra[KAKAO_PARAM_ORDER_ID] = order.order_id
    dataActionExtra[KAKAO_PARAM_PREV_BLOCK_ID] = KAKAO_BLOCK_USER_SET_ORDER_SHEET

    kakaoForm = KakaoForm()

    QUICKREPLIES_MAP = [
        {
            'action': 'block',
            'label': '홈으로 돌아가기',
            'messageText': '로딩중..',
            'blockId': KAKAO_BLOCK_USER_HOME,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_GET_MENU
            }
        },
    ]

    currentStock = order.menu.getCurrentStock()

    if(order.menu.max_stock <= order.menu.current_stock):

        kakaoForm.BasicCard_Push(
            '이 메뉴는 이미 매진됬습니다.',
            '아쉽지만 다른 메뉴를 주문해주세요!',
            {},
            []
        )
        kakaoForm.BasicCard_Add()

        kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)

        return JsonResponse(kakaoForm.GetForm())

    # Menu Carousel Card Add
    thumbnails = [
        {
            'imageUrl': '{}{}'.format(HOST_URL, menu.imgURL()),
            'fixedRatio': 'true',
            'width': 800,
            'height': 800,
        }
    ]

    isCafe = store.category.filter(name="카페").exists()
    if(isCafe):
        profile = {
            'nickname': '픽업 시간 : {pickup_time}'.format(pickup_time=dateByTimeZone(order.pickup_time).strftime(
                '%-m월 %-d일 오전 11시 30분 ~ 오후 4시')),
            'imageUrl': '{}{}'.format(HOST_URL, store.logoImgURL()),
        }
    else:
        profile = {
            'nickname': '픽업 시간 : {pickup_time}'.format(pickup_time=order.pickup_time.strftime(
                '%p %-I시 %-M분').replace('AM', '오전').replace('PM', '오후'),),
            'imageUrl': '{}{}'.format(HOST_URL, store.logoImgURL()),
        }

    kakaoMapUrl = 'https://map.kakao.com/link/map/{},{}'.format(
        store.name, menu.store.place)

    if(isB2BUser(user)):
        buttons = [
            {
                'action': 'block',
                'label': '주문 완료하기   ➔',
                'messageText': '로딩중..',
                'blockId': KAKAO_BLOCK_USER_SET_ORDER_SHEET,
                'extra': dataActionExtra,
            },
        ]

        kakaoForm.ComerceCard_Push(
            '',
            menu.price,
            None,
            thumbnails,
            profile,
            buttons
        )

        kakaoForm.ComerceCard_Add()
        kakaoForm.BasicCard_Push(
            '\'주문 완료하기\' 버튼을 꼭 눌러주세요!',
            '10시 30분 이후에는 주문이 되지 않습니다. 마감시간에 주의해주세요!',
            {},
            []
        )
        kakaoForm.BasicCard_Add()
    else:

        if(ORDERING_DEBUG_MODE):
            server_url = 'http://localhost:3000'
        else:
            server_url = 'https://www.eatple.com'

        buttons = [
            {
                'action': 'webLink',
                'label': '결제하러 가기   ➔',
                'messageText': '로딩중..',
                'extra': dataActionExtra,

                'webLinkUrl': '{server_url}/payment?merchant_uid={merchant_uid}&storeName={storeName}&menuName={menuName}&menuPrice={menuPrice}&buyer_name={buyer_name}&buyer_tel={buyer_tel}&buyer_email={buyer_email}'.format(
                    server_url=server_url,
                    merchant_uid=order.order_id,
                    storeName=store.name,
                    menuName=menu.name,
                    menuPrice=order.totalPrice,
                    buyer_name=user.app_user_id,
                    buyer_tel=str(user.phone_number)[3:13],
                    buyer_email=user.email,
                )
            },
        ]

        kakaoForm.ComerceCard_Push(
            '',
            menu.price,
            None,
            thumbnails,
            profile,
            buttons
        )

        kakaoForm.ComerceCard_Add()

        buttons = [
            {
                'action': 'block',
                'label': '잇플패스 확인',
                'messageText': '로딩중..',
                'blockId': KAKAO_BLOCK_USER_SET_ORDER_SHEET,
                'extra': dataActionExtra,
            },
        ]

        kakaoForm.BasicCard_Push(
            '결제가 완료되었다면 아래 \'잇플패스 확인\' 버튼을 눌러주세요.',
            '',
            {},
            buttons
        )

        kakaoForm.BasicCard_Add()

    GET_PICKUP_TIME_QUICKREPLIES_MAP = [
        {
            'action': 'message', 'label': '홈으로 돌아가기',
            'messageText': '로딩중..',
            'blockId': KAKAO_BLOCK_USER_HOME,
            'extra': {}
        },
    ]

    kakaoForm.QuickReplies_AddWithMap(GET_PICKUP_TIME_QUICKREPLIES_MAP)

    return JsonResponse(kakaoForm.GetForm())


def kakaoView_OrderPaymentCheck(kakaoPayload):
    # Block Validation
    prev_block_id = prevBlockValidation(kakaoPayload)
    if(prev_block_id != KAKAO_BLOCK_USER_SET_ORDER_SHEET):
        return errorView('잘못된 블럭 경로', '정상적이지 않은 경로거나, 오류가 발생했습니다.\n다시 주문해주세요!')

    # User Validation
    user = userValidation(kakaoPayload)
    if (user == None):
        return errorView('잘못된 블럭 경로', '정상적이지 않은 경로거나, 잘못된 계정입니다.')

    store = storeValidation(kakaoPayload)
    menu = menuValidation(kakaoPayload)
    order = orderValidation(kakaoPayload)

    if(order.store != store or order.menu != menu):
        return kakaoView_OrderPayment(kakaoPayload)

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

    if(store == None or menu == None or order == None):
        return errorView('잘못된 블럭 경로', '정상적이지 않은 경로거나, 오류가 발생했습니다.\n다시 주문해주세요!')

    # Order Record
    try:
        orderRecordSheet = OrderRecordSheet.objects.latest('update_date')
    except OrderRecordSheet.DoesNotExist:
        orderRecordSheet = OrderRecordSheet()

    if (orderRecordSheet.timeoutValidation()):
        return kakaoView_TimeOut(KAKAO_BLOCK_USER_SET_ORDER_SHEET)

    orderRecordSheet.user = user
    orderRecordSheet.menu = menu
    orderRecordSheet.recordUpdate(ORDER_RECORD_PAYMENT)

    dataActionExtra = kakaoPayload.dataActionExtra
    dataActionExtra[KAKAO_PARAM_ORDER_ID] = order.order_id
    dataActionExtra[KAKAO_PARAM_PREV_BLOCK_ID] = KAKAO_BLOCK_USER_SET_ORDER_SHEET

    order.orderStatusUpdate()

    # B2B User Pass
    if(isB2BUser(user)):
        eatplePassStatus = eatplePassValidation(user)
        if(eatplePassStatus != None):
            return eatplePassStatus

        currentSellingTime = sellingTimeCheck()

        if (currentSellingTime == None):
            return errorView('Get Invalid Selling Time', '잘못된 주문 시간입니다.')
        elif currentSellingTime == SELLING_TIME_DINNER:
            '''
                @NOTE Dinner Time Close In Alpha 
            '''
            kakaoForm.BasicCard_Push(
                '오늘 점심은 이미 마감되었어요.',
                '내일 점심은 오늘 16:30부터 내일 10:30까지 주문하실 수 있어요.',
                {},
                []
            )
            kakaoForm.BasicCard_Add()

            kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)

            return JsonResponse(kakaoForm.GetForm())

        currentStock = menu.getCurrentStock()

        if(menu.max_stock <= menu.current_stock):
            kakaoForm.BasicCard_Push(
                '이 메뉴는 이미 매진됬습니다.',
                '아쉽지만 다른 메뉴를 주문해주세요!',
                {},
                []
            )
            kakaoForm.BasicCard_Add()

            kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)

            return JsonResponse(kakaoForm.GetForm())

        order.payment_status = IAMPORT_ORDER_STATUS_PAID
        order.save()

        return kakaoView_EatplePassIssuance(kakaoPayload)

    # Normal User
    else:
        if(order.payment_status == IAMPORT_ORDER_STATUS_PAID):
            return kakaoView_EatplePassIssuance(kakaoPayload)
        else:
            BTN_MAP = [
                {
                    'action': 'webLink',
                    'label': '결제하러 가기   ➔',
                    'messageText': '로딩중..',
                    'extra': dataActionExtra,

                    'webLinkUrl': 'https://www.eatple.com/payment?merchant_uid={merchant_uid}'.format(
                        merchant_uid=order.order_id,
                    )
                },
                {
                    'action': 'block',
                    'label': '잇플패스 확인',
                    'messageText': '로딩중..',
                    'blockId': KAKAO_BLOCK_USER_SET_ORDER_SHEET,
                    'extra': dataActionExtra,
                },
            ]

            QUICKREPLIES_MAP = [
                {
                    'action': 'message', 'label': '홈으로 돌아가기',
                    'messageText': '로딩중..',
                    'blockId': KAKAO_BLOCK_USER_HOME,
                    'extra': {}
                },
            ]

            thumbnail = {'imageUrl': ''}

            buttons = BTN_MAP

            kakaoForm.BasicCard_Push(
                '아직 결제가 완료되지 않았어요!',
                '{menu} - {price}원'.format(menu=menu.name,
                                           price=order.totalPrice),
                thumbnail,
                buttons
            )
            kakaoForm.BasicCard_Add()

            kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)

            return JsonResponse(kakaoForm.GetForm())


def kakaoView_EatplePassIssuance(kakaoPayload):
    try:
        # Block Validation
        prev_block_id = prevBlockValidation(kakaoPayload)
        if(prev_block_id != KAKAO_BLOCK_USER_SET_ORDER_SHEET):
            return errorView('잘못된 블럭 경로', '정상적이지 않은 경로거나, 오류가 발생했습니다.')

        # User Validation
        user = userValidation(kakaoPayload)
        if (user == None):
            return errorView('잘못된 블럭 경로', '정상적이지 않은 경로거나, 오류가 발생했습니다.\n다시 주문해주세요!')

        store = storeValidation(kakaoPayload)
        menu = menuValidation(kakaoPayload)
        order = orderValidation(kakaoPayload)
        if(order == None):
            return errorView('잘못된 블럭 경로', '정상적이지 않은 경로거나 이미 발급이 완료되었어요!')
        else:
            order.orderStatusUpdate()

        orderManager = UserOrderManager(user)
        orderManager.orderPenddingCleanUp()

        # Order Record
        try:
            orderRecordSheet = OrderRecordSheet.objects.latest('update_date')
        except OrderRecordSheet.DoesNotExist:
            orderRecordSheet = OrderRecordSheet()

        if (orderRecordSheet.timeoutValidation()):
            return kakaoView_TimeOut(KAKAO_BLOCK_USER_SET_ORDER_SHEET)

        orderRecordSheet.user = user
        orderRecordSheet.menu = menu
        orderRecordSheet.paid = True
        orderRecordSheet.recordUpdate(ORDER_RECORD_PAYMENT_COMPLETED)

        dataActionExtra = kakaoPayload.dataActionExtra
        dataActionExtra[KAKAO_PARAM_ORDER_ID] = order.order_id
        dataActionExtra[KAKAO_PARAM_PREV_BLOCK_ID] = KAKAO_BLOCK_USER_SET_ORDER_SHEET

        order.payment_date = dateNowByTimeZone()
        order.save()

        kakaoForm = KakaoForm()

        thumbnail = {
            'imageUrl': '{}{}'.format(HOST_URL, EATPLE_PASS_IMG_01),
        }

        kakaoMapUrl = 'https://map.kakao.com/link/map/{},{}'.format(
            order.store.name,
            order.store.place
        )

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
            {
                'action': 'block',
                'label': '부탁하기',
                'messageText': '로딩중..',
                'blockId': KAKAO_BLOCK_USER_ORDER_SHARING_START,
                'extra': {
                    KAKAO_PARAM_ORDER_ID: order.order_id,
                    KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_EATPLE_PASS
                }
            },
        ]

        isCafe = store.category.filter(name="카페").exists()
        if(isCafe):
            pickupTimeStr = dateByTimeZone(order.pickup_time).strftime(
                '%-m월 %-d일 오전 11시 30분 ~ 오후 4시')
        else:
            buttons.append({
                'action': 'block',
                'label': '픽업시간 변경',
                'messageText': '로딩중..',
                'blockId': KAKAO_BLOCK_USER_EDIT_PICKUP_TIME,
                'extra': {
                    KAKAO_PARAM_ORDER_ID: order.order_id,
                    KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_EATPLE_PASS
                }
            })
            pickupTimeStr = dateByTimeZone(order.pickup_time).strftime(
                '%-m월 %-d일 %p %-I시 %-M분').replace('AM', '오전').replace('PM', '오후')

        kakaoForm.BasicCard_Push(
            '잇플패스 발급이 완료되었습니다.',
            '',
            {},
            []
        )
        kakaoForm.BasicCard_Add()

        kakaoForm.BasicCard_Push(
            '{}'.format(order.menu.name),
            '주문번호: {}\n - 주문자: {}({})\n\n - 매장: {}\n\n - 총 금액: {}원\n\n - 픽업 시간: {}'.format(
                order.order_id,
                order.ordersheet.user.nickname,
                str(order.ordersheet.user.phone_number)[9:13],
                order.store.name,
                order.totalPrice,
                pickupTimeStr,
            ),
            thumbnail,
            buttons
        )
        kakaoForm.BasicCard_Add()

        kakaoForm.BasicCard_Push(
            '{}'.format(order.store.addr),
            '',
            {},
            [
                {
                    'action': 'webLink',
                    'label': '위치보기',
                    'webLinkUrl': kakaoMapUrl
                },
            ]
        )
        kakaoForm.BasicCard_Add()

        QUICKREPLIES_MAP = [
            {
                'action': 'block',
                'label': '홈으로 돌아가기',
                'messageText': '로딩중..',
                'blockId': KAKAO_BLOCK_USER_HOME,
                'extra': {
                    KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_SET_ORDER_SHEET
                }
            },
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
        ]

        kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)

        return JsonResponse(kakaoForm.GetForm())

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView('{}'.format(ex))


def kakaoView_TimeOut(blockId):
    kakaoForm = KakaoForm()

    QUICKREPLIES_MAP = [
        {
            'action': 'block',
            'label': '홈으로 돌아가기',
            'messageText': '로딩중..',
            'blockId': KAKAO_BLOCK_USER_HOME,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: blockId
            }
        },
    ]

    kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)

    kakaoForm.SimpleText_Add(
        '주문시간이 초과되었습니다.'
    )

    return JsonResponse(kakaoForm.GetForm())

# # # # # # # # # # # # # # # # # # # # # # # # #
#
# External View
#
# # # # # # # # # # # # # # # # # # # # # # # # #


@csrf_exempt
def GET_Menu(request):
    EatplusSkillLog('Get Menu')

    kakaoPayload = KakaoPayLoad(request)

    # User Validation
    user = userValidation(kakaoPayload)
    if (user == None):
        return GET_UserHome(request)

    return kakaoView_MenuListup(kakaoPayload)


@csrf_exempt
def SET_PickupTime(request):
    EatplusSkillLog('Get PickupTime')

    try:
        kakaoPayload = KakaoPayLoad(request)

        # User Validation
        user = userValidation(kakaoPayload)
        if (user == None):
            return GET_UserHome(request)

        return kakaoView_PickupTime(kakaoPayload)
    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView('{}'.format(ex))


@csrf_exempt
def SET_OrderSheet(request):
    EatplusSkillLog('Order Sheet Check')
    try:
        kakaoPayload = KakaoPayLoad(request)

        # User Validation
        user = userValidation(kakaoPayload)
        if (user == None):
            return GET_UserHome(request)

        # Block Validation
        prev_block_id = prevBlockValidation(kakaoPayload)
        if(prev_block_id != KAKAO_BLOCK_USER_SET_PICKUP_TIME and prev_block_id != KAKAO_BLOCK_USER_SET_ORDER_SHEET):
            return errorView('잘못된 블럭 경로', '정상적이지 않은 경로거나, 오류가 발생했습니다.\n다시 주문해주세요!')

        if(prev_block_id == KAKAO_BLOCK_USER_SET_PICKUP_TIME):
            return kakaoView_OrderPayment(kakaoPayload)
        elif(prev_block_id == KAKAO_BLOCK_USER_SET_ORDER_SHEET):
            return kakaoView_OrderPaymentCheck(kakaoPayload)

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView('{}'.format(ex))
