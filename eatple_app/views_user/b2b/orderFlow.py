# View-System
from eatple_app.views_system.include import *
from eatple_app.views_system.debugger import *

from eatple_app.views import GET_UserHome, GET_EatplePass


# STATIC CONFIG
MENU_LIST_LENGTH = 20
DEFAULT_DISTANCE_CONDITION = 800
DEFAULT_AREA_IN_FLAG = True
DEFAULT_AREA_CODE = None

SERVICE_AREAS = {
    'yeoksam': {
        'name': '역삼',
        'y': 37.500682,
        'x': 127.036598
    },
    'sinsa': {
        'name': '신사',
        'y': 37.516433,
        'x': 127.020389
    },
    'samsung': {
        'name': '삼성',
        'y': 37.508845,
        'x': 127.063132
    },
    'gangnam': {
        'name': '강남',
        'y': 37.497899,
        'x': 127.027670
    },
}

# # # # # # # # # # # # # # # # # # # # # # # # #
#
# Static View
#
# # # # # # # # # # # # # # # # # # # # # # # # #


def isPurchase(user, sellingTime, kakaoPayload):
    orderManager = UserOrderManager(user)
    orderManager.orderPaidCheck()

    orderManager.availableOrderStatusUpdate()

    lunchPurchaed = orderManager.getAvailableLunchOrder().filter(
        ordersheet__user=user).exists()
    dinnerPurchaced = orderManager.getAvailableDinnerOrder().filter(
        ordersheet__user=user).exists()

    kakaoForm = KakaoForm()

    kakaoForm.QuickReplies_AddWithMap(DEFAULT_QUICKREPLIES_MAP)

    if (lunchPurchaed or dinnerPurchaced):
        return GET_EatplePass(kakaoPayload.request)

    elif (lunchPurchaed):
        return GET_EatplePass(kakaoPayload.request)

    elif (dinnerPurchaced):
        return GET_EatplePass(kakaoPayload.request)

    return None


def kakaoView_TimeOut(blockId):
    kakaoForm = KakaoForm()

    QUICKREPLIES_MAP = [
        {
            'action': 'block',
            'label': '🏠  홈',
            'messageText': '🏠  홈',
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


def kakaoView_MenuListup(kakaoPayload):
    kakaoForm = KakaoForm()

    # User Validation
    user = userValidation(kakaoPayload)
    if (user == None):
        return errorView('잘못된 사용자 계정', '찾을 수 없는 사용자 계정 아이디입니다.')

    order = orderValidation(kakaoPayload)
    if (order != None):
        order.store = None
        order.save()

        # Order Record
        try:
            orderRecordSheet = OrderRecordSheet.objects.get(order=order)
        except OrderRecordSheet.DoesNotExist:
            orderRecordSheet = OrderRecordSheet()

        if (orderRecordSheet.timeoutValidation()):
            orderRecordSheet.recordUpdate(user, order, ORDER_RECORD_TIMEOUT)
            return kakaoView_TimeOut(KAKAO_BLOCK_USER_GET_STORE)
        else:
            orderRecordSheet.recordUpdate(user, order, ORDER_RECORD_GET_STORE)

        pass
    else:
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
        order.save()

        # Order Log Record Init
        orderRecordSheet = OrderRecordSheet()
        orderRecordSheet.recordUpdate(user, order, ORDER_RECORD_GET_STORE)

    # Order Record
    try:
        orderRecordSheet = OrderRecordSheet.objects.get(order=order)
    except OrderRecordSheet.DoesNotExist:
        orderRecordSheet = OrderRecordSheet()

    if (orderRecordSheet.timeoutValidation()):
        orderRecordSheet.recordUpdate(user, order, ORDER_RECORD_TIMEOUT)
        return kakaoView_TimeOut(KAKAO_BLOCK_USER_SET_PICKUP_TIME)
    else:
        orderRecordSheet.recordUpdate(user, order, ORDER_RECORD_GET_MENU)

    # @BETA Dinner Beta
    sellingTime = SELLING_TIME_LUNCH
    currentSellingTime = sellingTimeCheck()

    # User's Eatple Pass Validation
    eatplePassStatus = isPurchase(user, sellingTime, kakaoPayload)
    if(eatplePassStatus != None):
        return eatplePassStatus

    QUICKREPLIES_MAP = [
        {
            'action': 'block',
            'label': '🏠  홈',
            'messageText': '🏠  홈',
            'blockId': KAKAO_BLOCK_USER_HOME,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_GET_MENU
            }
        },
    ]

    distance_condition = DEFAULT_DISTANCE_CONDITION
    area_in_flag = DEFAULT_AREA_IN_FLAG
    area_code = DEFAULT_AREA_CODE

    menuList = Menu.objects.annotate(
        # distance=Distance(F('store__place__point'),
        #                  user.location.point) * 100 * 1000,
        distance=Distance(F('store__place__point'),
                          user.company.companyplace.point) * 100 * 1000,
    ).filter(
        ~Q(tag__name__contains='픽업존') &
        Q(selling_time=sellingTime) &
        (
            Q(store__type=STORE_TYPE_B2B_AND_NORMAL) |
            Q(store__type=STORE_TYPE_B2B)
        ) &
        (
            Q(type=MENU_TYPE_B2B_AND_NORMAL) |
            Q(type=STORE_TYPE_B2B)
        ) &
        Q(status=OC_OPEN) &
        (
            Q(store__status=OC_OPEN) |
            Q(store__status=STORE_OC_VACATION)
        )
    ).order_by(F'price')

    menuList = menuList.filter(Q(distance__lte=distance_condition))

    sellingOutList = []

    if menuList:
        KakaoInstantForm().Message(
            '하단의 메뉴중 하나를 선택해주세요.',
            '',
            kakaoForm=kakaoForm
        )

        # Menu Carousel Card Add
        for menu in menuList:
            currentStock = menu.getCurrentStock()

            if(menu.max_stock > menu.current_stock):
                thumbnail = {
                    'imageUrl': '{}{}'.format(HOST_URL, menu.imgURL()),
                    'fixedRatio': 'true',
                    'width': 80,
                    'height': 800,
                }

                buttons = [
                    {
                        'action': 'block',
                        'label': '선택',
                        'messageText': KAKAO_EMOJI_LOADING,
                        'blockId': KAKAO_BLOCK_USER_SET_PICKUP_TIME,
                        'extra': {
                            KAKAO_PARAM_SELLING_TIME: sellingTime,
                            KAKAO_PARAM_STORE_ID: menu.store.store_id,
                            KAKAO_PARAM_MENU_ID: menu.menu_id,
                            KAKAO_PARAM_ORDER_ID: order.order_id,
                            KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_GET_MENU
                        }
                    },
                ]

                kakaoForm.BasicCard_Push(
                    '{}'.format(menu.store.name),
                    '{}'.format(menu.description),
                    thumbnail,
                    buttons
                )
            else:  # selling out
                sellingOutList.extend(list(Menu.objects.filter(id=menu.id)))

        for menu in sellingOutList:
            delivery = menu.tag.filter(name='픽업존').exists()

            if(delivery):
                status = '픽업존'
            else:
                status = '매진'

            kakaoMapUrl = 'https://map.kakao.com/link/map/{name},{place}'.format(
                name=menu.store.name,
                place=menu.store.place
            )
            if(menu.store.status == STORE_OC_VACATION):
                thumbnail = {
                    'imageUrl': '{}{}'.format(HOST_URL, menu.imgURL()),
                    'fixedRatio': 'true',
                    'width': 800,
                    'height': 800,
                }
                buttons = [
                ]

                KakaoInstantForm().MenuList(
                    menu,
                    '휴무중',
                    thumbnail,
                    buttons,
                    kakaoForm
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
                        'webLinkUrl': kakaoMapUrl,
                    },
                ]

                KakaoInstantForm().MenuList(
                    menu,
                    status,
                    thumbnail,
                    buttons,
                    kakaoForm
                )

        kakaoForm.BasicCard_Add(None)

        if(
            (currentSellingTime == sellingTime) and
            (weekendTimeCheck(sellingTime) == False)
        ):
            KakaoInstantForm().Message(
                '🟢  주문 가능 시간입니다.',
                '마감되기 전에 얼른 주문하세요.',
                kakaoForm=kakaoForm
            )
        else:
            KakaoInstantForm().Message(
                '🔴  주문 가능 시간이 아닙니다.',
                '메뉴는 자유롭게 볼 수 있어요.',
                kakaoForm=kakaoForm
            )
    else:
        KakaoInstantForm().Message(
            '판매중인 메뉴가 없습니다.',
            '빠른 시일안에 이 지역 매장을 늘려볼게요.',
            kakaoForm=kakaoForm
        )

    kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)

    return JsonResponse(kakaoForm.GetForm())


def kakaoView_PickupTime(kakaoPayload):
    kakaoForm = KakaoForm()

    # Block Validation
    prev_block_id = prevBlockValidation(kakaoPayload)
    if(prev_block_id != KAKAO_BLOCK_USER_GET_MENU and
            prev_block_id != KAKAO_BLOCK_USER_SET_ORDER_SHEET):
        return errorView('잘못된 블럭 경로', '정상적이지 않은 블럭 경로입니다.')

    # User Validation
    user = userValidation(kakaoPayload)
    if (user == None):
        return errorView('잘못된 사용자 계정', '찾을 수 없는 사용자 계정 아이디입니다.')

    order = orderValidation(kakaoPayload)
    if(order == None):
        return errorView('잘못된 주문 번호', '잘못된 주문 번호입니다.')

    # @BETA Dinner Beta
    sellingTime = sellingTimeValidation(kakaoPayload)

    # User's Eatple Pass Validation
    eatplePassStatus = isPurchase(user, sellingTime, kakaoPayload)
    if(eatplePassStatus != None):
        return eatplePassStatus

    store = storeValidation(kakaoPayload)
    menu = menuValidation(kakaoPayload)
    if(store == None or menu == None):
        return errorView('잘못된 주문 내역', '잘못된 주문 정보입니다.')

    QUICKREPLIES_MAP = [
        {
            'action': 'block',
            'label': '🏠  홈',
            'messageText': '🏠  홈',
            'blockId': KAKAO_BLOCK_USER_HOME,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_GET_MENU
            }
        },
        {
            'action': 'block',
            'label': '뒤로가기',
            'messageText': KAKAO_EMOJI_LOADING,
            'blockId': KAKAO_BLOCK_USER_GET_STORE,
            'extra': {
                KAKAO_PARAM_SELLING_TIME: sellingTime,
                KAKAO_PARAM_STORE_ID: store.store_id,
                KAKAO_PARAM_STORE_ID: store.store_id,
                KAKAO_PARAM_ORDER_ID: order.order_id,
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_GET_MENU
            }
        },
    ]

    # Order Record
    try:
        orderRecordSheet = OrderRecordSheet.objects.get(order=order)
    except OrderRecordSheet.DoesNotExist:
        orderRecordSheet = OrderRecordSheet()

    if (orderRecordSheet.timeoutValidation()):
        orderRecordSheet.recordUpdate(user, order, ORDER_RECORD_TIMEOUT)
        return kakaoView_TimeOut(KAKAO_BLOCK_USER_SET_PICKUP_TIME)
    else:
        orderRecordSheet.recordUpdate(
            user, order, ORDER_RECORD_SET_PICKUP_TIEM)

    currentStock = menu.getCurrentStock()

    if(menu.max_stock <= menu.current_stock):
        KakaoInstantForm().Message(
            '⛔  이 메뉴는 이미 매진됬습니다.',
            '아쉽지만 다른 메뉴를 주문해주세요.',
            kakaoForm=kakaoForm
        )

        kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)

        return JsonResponse(kakaoForm.GetForm())

    isVacationDay = vacationTimeCheck()
    isLunchClosedDay = weekendTimeCheck(SELLING_TIME_LUNCH)
    isDinnerClosedDay = weekendTimeCheck(SELLING_TIME_DINNER)

    if(isVacationDay):
        KakaoInstantForm().Message(
            '📌  안내사항',
            '잇플 휴무일입니다.',
            kakaoForm=kakaoForm
        )

        kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)

        return JsonResponse(kakaoForm.GetForm())

    if((sellingTime == SELLING_TIME_LUNCH) and isLunchClosedDay):
        KakaoInstantForm().Message(
            '📌  안내사항',
            '월요일 점심 주문은 일요일 오후 9시부터 가능합니다.',
            kakaoForm=kakaoForm
        )

        kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)

        return JsonResponse(kakaoForm.GetForm())

    if((sellingTime == SELLING_TIME_DINNER) and isDinnerClosedDay):
        KakaoInstantForm().Message(
            '📌  안내사항',
            '월요일 저녁 주문은 월요일 오후 2시부터 가능합니다.',
            kakaoForm=kakaoForm
        )

        kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)

        return JsonResponse(kakaoForm.GetForm())

    if(sellingTimeCheck() == None):
        currentSellingTime = sellingTimeCheck(True)

        if (currentSellingTime == None):
            return errorView('잘못된 주문 시간', '정상적인 주문 시간대가 아닙니다.')

        if (currentSellingTime == SELLING_TIME_DINNER):
            KakaoInstantForm().Message(
                '🔴  현재는 주문 가능 시간이 아닙니다.',
                '점심(당일) - 마감되었습니다.',
                kakaoForm=kakaoForm
            )
            kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)

            return JsonResponse(kakaoForm.GetForm())
        elif (currentSellingTime == SELLING_TIME_LUNCH):
            KakaoInstantForm().Message(
                '🔴  현재는 주문 가능 시간이 아닙니다.',
                '점심(내일) - 오늘 오후 9시부터',
                kakaoForm=kakaoForm
            )

            kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)

            return JsonResponse(kakaoForm.GetForm())
    else:
        currentSellingTime = sellingTimeCheck()

        if(sellingTime != currentSellingTime):
            KakaoInstantForm().Message(
                '🔴  오늘 점심은 이미 마감되었어요.',
                '점심(내일) - 오늘 오후 9시부터',
                kakaoForm=kakaoForm
            )

            kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)

            return JsonResponse(kakaoForm.GetForm())

    PICKUP_TIME_QUICKREPLIES_MAP = []

    pickupTimes = menu.pickup_time.filter(selling_time=currentSellingTime)

    order = orderValidation(kakaoPayload)

    isCafe = store.category.filter(name='카페').exists()
    if(isCafe):
        KakaoInstantForm().Message(
            '🛎  상시픽업이 가능한 매장입니다.',
            '오전 11시 30분 부터 오후 2시 까지 언제든 방문하여 메뉴를 픽업할 수 있습니다.',
            kakaoForm=kakaoForm
        )
    else:
        if(pickupTimes.count() < 2):
            KakaoInstantForm().Message(
                '❗ 픽업 시간이 제한된 매장입니다',
                '점주님의 요청으로 픽업 시간이 한 타임으로 제한된 매장입니다.',
                kakaoForm=kakaoForm
            )

    KakaoInstantForm().Message(
        '픽업 시간을 선택 해주세요.',
        '{} - {}'.format(menu.store.name, menu.name),
        kakaoForm=kakaoForm
    )

    orderTimeTable = OrderTimeSheet()

    if(isCafe):
        dataActionExtra = {
            KAKAO_PARAM_SELLING_TIME: sellingTime,
            KAKAO_PARAM_STORE_ID: menu.store.store_id,
            KAKAO_PARAM_MENU_ID: menu.menu_id,
            KAKAO_PARAM_ORDER_ID: order.order_id,
            KAKAO_PARAM_PICKUP_TIME: orderTimeTable.GetLunchOrderPickupTimeStart().strftime('%H:%M'),
            KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_SET_PICKUP_TIME
        }

        kakaoForm.QuickReplies_Add(
            'block',
            '오전 11시 30분 ~ 오후 2시',
            KAKAO_EMOJI_LOADING,
            KAKAO_BLOCK_USER_SET_ORDER_SHEET,
            dataActionExtra
        )
    else:
        for pickupTime in pickupTimes:
            dataActionExtra = {
                KAKAO_PARAM_SELLING_TIME: sellingTime,
                KAKAO_PARAM_STORE_ID: menu.store.store_id,
                KAKAO_PARAM_MENU_ID: menu.menu_id,
                KAKAO_PARAM_ORDER_ID: order.order_id,
                KAKAO_PARAM_PICKUP_TIME: pickupTime.time.strftime('%H:%M'),
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_SET_PICKUP_TIME
            }

            if(order != None):
                dataActionExtra[KAKAO_PARAM_ORDER_ID] = order.order_id

            if(pickupTime.time.minute == 0):
                pickupTimeQR = '{}'.format(pickupTime.time.strftime(
                    '%p %-I시').replace('AM', '오전').replace('PM', '오후'))
            else:
                pickupTimeQR = '{}'.format(pickupTime.time.strftime(
                    '%p %-I시 %M분').replace('AM', '오전').replace('PM', '오후'))

            kakaoForm.QuickReplies_Add(
                'block',
                pickupTimeQR,
                KAKAO_EMOJI_LOADING,
                KAKAO_BLOCK_USER_SET_ORDER_SHEET,
                dataActionExtra
            )

    return JsonResponse(kakaoForm.GetForm())


def kakaoView_OrderPayment(kakaoPayload):
    kakaoForm = KakaoForm()

    QUICKREPLIES_MAP = [
        {
            'action': 'block',
            'label': '🏠  홈',
            'messageText': '🏠  홈',
            'blockId': KAKAO_BLOCK_USER_HOME,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_GET_MENU
            }
        },
    ]

    # Block Validation
    prev_block_id = prevBlockValidation(kakaoPayload)
    if(prev_block_id != KAKAO_BLOCK_USER_SET_PICKUP_TIME and prev_block_id != KAKAO_BLOCK_USER_SET_ORDER_SHEET):
        return errorView('잘못된 블럭 경로', '정상적이지 않은 블럭 경로입니다.')

    # User Validation
    user = userValidation(kakaoPayload)
    if (user == None):
        return errorView('잘못된 사용자 계정', '찾을 수 없는 사용자 계정 아이디입니다.')

    # @BETA Dinner Beta
    sellingTime = sellingTimeValidation(kakaoPayload)

    # User's Eatple Pass Validation
    eatplePassStatus = isPurchase(user, sellingTime, kakaoPayload)
    if(eatplePassStatus != None):
        return eatplePassStatus

    store = storeValidation(kakaoPayload)
    menu = menuValidation(kakaoPayload)
    pickup_time = pickupTimeValidation(kakaoPayload)

    if(store == None or menu == None or pickup_time == None):
        return errorView('잘못된 주문 내역', '잘못된 주문 정보입니다.')

    order = orderValidation(kakaoPayload)
    if(order == None):
        return errorView('잘못된 주문 번호', '잘못된 주문 번호입니다.')
    else:
        order.user = user
        order.menu = menu
        order.store = store
        order.pickup_time = order.pickupTimeToDateTime(pickup_time)
        order.totalPrice = menu.price
        order.count = 1
        order.type = ORDER_TYPE_NORMAL
        # @TODO: NOW KAKAO PAY ONLY
        order.payment_type = ORDER_PAYMENT_KAKAO_PAY
        order.save()

    # Order Record
    try:
        orderRecordSheet = OrderRecordSheet.objects.get(order=order)
    except OrderRecordSheet.DoesNotExist:
        orderRecordSheet = OrderRecordSheet()

    if (orderRecordSheet.timeoutValidation()):
        orderRecordSheet.recordUpdate(user, order, ORDER_RECORD_TIMEOUT)
        return kakaoView_TimeOut(user, order, AKAO_BLOCK_USER_SET_ORDER_SHEET)
    else:
        orderRecordSheet.recordUpdate(
            user, order, ORDER_RECORD_ORDERSHEET_CHECK)

    dataActionExtra = kakaoPayload.dataActionExtra
    dataActionExtra[KAKAO_PARAM_ORDER_ID] = order.order_id
    dataActionExtra[KAKAO_PARAM_PREV_BLOCK_ID] = KAKAO_BLOCK_USER_SET_ORDER_SHEET

    currentStock = order.menu.getCurrentStock()

    if(order.menu.max_stock <= order.menu.current_stock):
        KakaoInstantForm().Message(
            '⛔  이 메뉴는 이미 매진됬습니다.',
            '아쉽지만 다른 메뉴를 주문해주세요.',
            kakaoForm=kakaoForm
        )

        kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)

        return JsonResponse(kakaoForm.GetForm())

    order.payment_type = ORDER_PAYMENT_PAY_PASS
    order.orderPay()

    if(order.payment_status == EATPLE_ORDER_STATUS_PAID):
        return kakaoView_EatplePassIssuance(kakaoPayload)

    return JsonResponse(kakaoForm.GetForm())


def kakaoView_EatplePassIssuance(kakaoPayload):
    try:
        kakaoForm = KakaoForm()

        QUICKREPLIES_MAP = [
            {
                'action': 'block',
                'label': '🏠  홈',
                'messageText': KAKAO_EMOJI_LOADING,
                'blockId': KAKAO_BLOCK_USER_HOME,
                'extra': {
                    KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_EDIT_PICKUP_TIME
                }
            },
        ]

        # Block Validation
        prev_block_id = prevBlockValidation(kakaoPayload)
        if(prev_block_id != KAKAO_BLOCK_USER_SET_ORDER_SHEET):
            return errorView('잘못된 블럭 경로', '정상적이지 않은 블럭 경로입니다.')

        # User Validation
        user = userValidation(kakaoPayload)
        if (user == None):
            return errorView('잘못된 사용자 계정', '찾을 수 없는 사용자 계정 아이디입니다.')

        order = orderValidation(kakaoPayload)
        if(order == None):
            return errorView('주문 상태 확인', '정상적이지 않은 경로거나 이미 발급이 완료되었어요.')
        else:
            pass
            # order.orderStatusUpdate()

        store = storeValidation(kakaoPayload)
        menu = menuValidation(kakaoPayload)
        if(store == None or menu == None):
            return errorView('결제 실패', '주문을 도중에 중단한 주문 번호 입니다.')

        if(order.payment_status != EATPLE_ORDER_STATUS_PAID):
            KakaoInstantForm().Message(
                '주문에 실패하였습니다.',
                '죄송하지만 처음부터 다시 주문해주세요..',
                kakaoForm=kakaoForm
            )

            kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)

            return JsonResponse(kakaoForm.GetForm())

        orderManager = UserOrderManager(user)
        orderManager.orderPaidCheck()
        orderManager.orderPenddingCleanUp()

        # Order Record
        try:
            orderRecordSheet = OrderRecordSheet.objects.get(order=order)
        except OrderRecordSheet.DoesNotExist:
            orderRecordSheet = OrderRecordSheet()

        orderRecordSheet.paid = True
        orderRecordSheet.recordUpdate(
            user, order, ORDER_RECORD_PAYMENT_COMPLETED)

        dataActionExtra = kakaoPayload.dataActionExtra
        dataActionExtra[KAKAO_PARAM_ORDER_ID] = order.order_id
        dataActionExtra[KAKAO_PARAM_PREV_BLOCK_ID] = KAKAO_BLOCK_USER_SET_ORDER_SHEET

        KakaoInstantForm().Message(
            '주문이 완료되었습니다.',
            kakaoForm=kakaoForm
        )

        KakaoInstantForm().EatplePassIssued(
            order,
            kakaoForm,
        )

        return JsonResponse(kakaoForm.GetForm())

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView('{}'.format(ex))

# # # # # # # # # # # # # # # # # # # # # # # # #
#
# External View
#
# # # # # # # # # # # # # # # # # # # # # # # # #


@csrf_exempt
def GET_B2B_Store(request):
    EatplusSkillLog('GET_B2B_Store')

    kakaoPayload = KakaoPayLoad(request)

    # User Validation
    user = userValidation(kakaoPayload)
    if (user == None):
        return GET_UserHome(request)

    return kakaoView_MenuListup(kakaoPayload)


@csrf_exempt
def GET_B2B_Menu(request):
    EatplusSkillLog('GET_B2B_Menu')

    kakaoPayload = KakaoPayLoad(request)

    # User Validation
    user = userValidation(kakaoPayload)
    if (user == None):
        return GET_UserHome(request)

    # User Case
    return kakaoView_MenuListup(kakaoPayload)


@csrf_exempt
def SET_B2B_PickupTime(request):
    EatplusSkillLog('SET_B2B_PickupTime')

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
def SET_B2B_OrderSheet(request):
    EatplusSkillLog('SET_B2B_OrderSheet')

    try:
        kakaoPayload = KakaoPayLoad(request)

        # User Validation
        user = userValidation(kakaoPayload)
        if (user == None):
            return GET_UserHome(request)

        # Block Validation
        prev_block_id = prevBlockValidation(kakaoPayload)
        if(prev_block_id != KAKAO_BLOCK_USER_SET_PICKUP_TIME and prev_block_id != KAKAO_BLOCK_USER_SET_ORDER_SHEET):
            return errorView('잘못된 블럭 경로', '정상적이지 않은 경로거나, 오류가 발생했습니다.\n다시 주문해주세요.')

        return kakaoView_OrderPayment(kakaoPayload)

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView('{}'.format(ex))
