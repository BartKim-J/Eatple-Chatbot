# View-System
from eatple_app.views_system.include import *
from eatple_app.views_system.debugger import *

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

    # User Validation
    user = userValidation(kakaoPayload)
    if (user == None):
        return errorView('잘못된 사용자 계정', '찾을 수 없는 사용자 계정 아이디입니다.')

    # User's Eatple Pass Validation
    eatplePassStatus = eatplePassValidation(user)
    if(eatplePassStatus != None):
        return eatplePassStatus

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

    # Order Log Record
    orderRecordSheet = OrderRecordSheet()
    orderRecordSheet.user = user
    orderRecordSheet.order = order
    orderRecordSheet.recordUpdate(ORDER_RECORD_GET_MENU)

    # @BETA alway show lunch menu
    # currentSellingTime = sellingTimeCheck()
    currentSellingTime = SELLING_TIME_LUNCH

    distance_condition = DEFAULT_DISTANCE_CONDITION
    area_in_flag = DEFAULT_AREA_IN_FLAG
    area_code = DEFAULT_AREA_CODE

    try:
        distance_condition = kakaoPayload.dataActionExtra['distance_condition']
        area_in_flag = kakaoPayload.dataActionExtra['area_in_flag']
        area_code = kakaoPayload.dataActionExtra['area']

        QUICKREPLIES_MAP.insert(0, {
            'action': 'block',
            'label': '내 지역',
            'messageText': KAKAO_EMOJI_LOADING,
            'blockId': KAKAO_BLOCK_USER_GET_MENU,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_GET_MENU,
                'distance_condition': DEFAULT_DISTANCE_CONDITION,
                'area_in_flag': True,
            }
        })
    except Exception as ex:
        for code, area in SERVICE_AREAS.items():
            QUICKREPLIES_MAP.insert(0, {
                'action': 'block',
                'label': '{}역'.format(area['name']),
                'messageText': KAKAO_EMOJI_LOADING,
                'blockId': KAKAO_BLOCK_USER_GET_MENU,
                'extra': {
                    KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_GET_MENU,
                    'distance_condition': DEFAULT_DISTANCE_CONDITION,
                    'area_in_flag': False,
                    'area': code
                }
            })

    menuList = Menu.objects.annotate(
        distance=Distance(F('store__place__point'),
                          user.location.point) * 100 * 1000,
        pickupzone=Count(Case(
            When(
                tag__name="픽업존",
                then=1
            ),
            default=0,
            output_field=BooleanField(),
        )),
    ).filter(
        Q(selling_time=currentSellingTime) &
        (
            Q(store__type=STORE_TYPE_B2B_AND_NORMAL) |
            Q(store__type=STORE_TYPE_NORMAL)
        ) &
        (
            Q(type=MENU_TYPE_B2B_AND_NORMAL) |
            Q(type=MENU_TYPE_NORMAL)
        ) &
        Q(status=OC_OPEN) &
        (
            Q(store__status=OC_OPEN) |
            Q(store__status=STORE_OC_VACATION)
        )
    ).order_by(F'-pickupzone', F'distance', F'price')

    # @PROMOTION
    addressMap = user.location.address.split()

    if(area_in_flag):
        if(addressMap[2] == "신사동" or area_code == "sinsa"):
            pickupZoneMenuList = menuList.filter(Q(tag__name="픽업존"))
            menuList = menuList.filter(
                ~Q(tag__name="픽업존") &
                Q(distance__lt=distance_condition)
            )
            menuList = menuList | pickupZoneMenuList
            header = {
                "title": None,
                "description": None,
                "thumbnail": {
                    "imageUrl": '{}{}'.format(HOST_URL, EATPLE_MENU_HEADER_FF_IMG)
                }
            }
        else:
            menuList = menuList.filter(Q(distance__lt=distance_condition))
            header = None
    else:
        # @PROMOTION
        menuList = menuList.annotate(
            distance=Distance(
                F('store__place__point'),
                Point(y=SERVICE_AREAS[area_code]['y'], x=SERVICE_AREAS[area_code]['x'], srid=4326)) * 100 * 1000,
        )
        if(area_code == "sinsa"):
            pickupZoneMenuList = menuList.filter(Q(tag__name="픽업존"))
            menuList = menuList.filter(
                ~Q(tag__name="픽업존") &
                Q(distance__lt=distance_condition)
            )
            menuList = menuList | pickupZoneMenuList

            header = {
                "title": None,
                "description": None,
                "thumbnail": {
                    "imageUrl": '{}{}'.format(HOST_URL, EATPLE_MENU_HEADER_FF_IMG)
                }
            }
        else:
            menuList = menuList.filter(
                Q(distance__lte=distance_condition) &
                ~Q(tag__name="픽업존")
            )

            header = None

    sellingOutList = []

    if menuList:
        KakaoInstantForm().Message(
            '※ 메뉴 선택과 픽업 시간 선택을 해주세요.',
            kakaoForm=kakaoForm
        )

        # Menu Carousel Card Add
        for menu in menuList:
            currentStock = menu.getCurrentStock()

            if(menu.max_stock > menu.current_stock and menu.store.status == STORE_OC_OPEN):
                delivery = menu.tag.filter(name="픽업존").exists()
                distance = menu.distance
                walkTime = round((distance / 100) * 2.1)

                if(delivery):
                    walkTime = '픽업존'
                elif(distance <= distance_condition):
                    if(area_in_flag):
                        walkTime = '약 도보 {} 분'.format(walkTime)
                    else:
                        walkTime = '약 도보 {} 분( {}역 )'.format(
                            walkTime, SERVICE_AREAS[area_code]['name'])
                else:
                    walkTime = '1 ㎞ 이상'

                thumbnail = {
                    'imageUrl': '{}{}'.format(HOST_URL, menu.imgURL()),
                    'fixedRatio': 'true',
                    'width': 80,
                    'height': 800,
                }

                kakaoMapUrl = 'https://map.kakao.com/link/map/{name},{place}'.format(
                    name=menu.store.name,
                    place=menu.store.place
                )

                if(delivery == False):
                    buttons = [
                        {
                            'action': 'block',
                            'label': '선택',
                            'messageText': KAKAO_EMOJI_LOADING,
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
                            'webLinkUrl': kakaoMapUrl,
                        }
                    ]
                else:
                    buttons = [
                        {
                            'action': 'block',
                            'label': '픽업존에서 수령하기',
                            'messageText': KAKAO_EMOJI_LOADING,
                            'blockId': KAKAO_BLOCK_USER_SET_PICKUP_TIME,
                            'extra': {
                                KAKAO_PARAM_STORE_ID: menu.store.store_id,
                                KAKAO_PARAM_MENU_ID: menu.menu_id,
                                KAKAO_PARAM_ORDER_ID: order.order_id,
                                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_GET_MENU
                            }
                        },
                    ]

                KakaoInstantForm().MenuList(
                    menu,
                    walkTime,
                    thumbnail,
                    buttons,
                    kakaoForm
                )

            else:  # selling out
                sellingOutList.extend(list(Menu.objects.filter(id=menu.id)))

        for menu in sellingOutList:
            delivery = menu.tag.filter(name="픽업존").exists()

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
                    {
                        'action': 'webLink',
                        'label': '위치보기',
                        'webLinkUrl': kakaoMapUrl,
                    },
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

        kakaoForm.ComerceCard_Add(header)

    else:
        KakaoInstantForm().Message(
            '판매중인 메뉴가 없습니다.',
            '빠른 시일안에 이 지역 점포를 늘려볼게요!',
            kakaoForm=kakaoForm
        )

    kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)

    return JsonResponse(kakaoForm.GetForm())


def kakaoView_MenuListupWithAreaOut(kakaoPayload):
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

    # User Validation
    user = userValidation(kakaoPayload)
    if (user == None):
        return errorView('잘못된 사용자 계정', '찾을 수 없는 사용자 계정 아이디입니다.')

    # @BETA alway show lunch menu
    # currentSellingTime = sellingTimeCheck()
    currentSellingTime = SELLING_TIME_LUNCH

    menuList = Menu.objects.annotate(
        distance=Distance(F('store__place__point'),
                          user.location.point) * 100 * 1000,
    ).filter(
        Q(selling_time=currentSellingTime) &
        (
            Q(store__type=STORE_TYPE_B2B_AND_NORMAL) |
            Q(store__type=STORE_TYPE_NORMAL)
        ) &
        (
            Q(type=MENU_TYPE_B2B_AND_NORMAL) |
            Q(type=MENU_TYPE_NORMAL)
        ) &
        Q(status=OC_OPEN) &
        (
            Q(store__status=OC_OPEN) |
            Q(store__status=STORE_OC_VACATION)
        )
    ).order_by(F'distance')

    if menuList:
        KakaoInstantForm().Message(
            '설정한 지역은 서비스 지역이 아닙니다.',
            '서비스 지역 - 강남, 역삼, 삼성, 신사',
            kakaoForm=kakaoForm
        )

        # Menu Carousel Card Add
        for menu in menuList:
            currentStock = menu.getCurrentStock()

            if(menu.store.status == STORE_OC_OPEN):
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
                    "서비스 지역 아님",
                    thumbnail,
                    buttons,
                    kakaoForm
                )

        kakaoForm.ComerceCard_Add()

    else:
        KakaoInstantForm().Message(
            '판매중인 메뉴가 없습니다.',
            '빠른 시일안에 이 지역 점포를 늘려볼게요!',
            kakaoForm=kakaoForm
        )

    kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)

    return JsonResponse(kakaoForm.GetForm())


def kakaoView_PickupTime(kakaoPayload):
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
    if(prev_block_id != KAKAO_BLOCK_USER_GET_MENU and
            prev_block_id != KAKAO_BLOCK_USER_SET_ORDER_SHEET):
        return errorView('잘못된 블럭 경로', '정상적이지 않은 블럭 경로입니다.')

    # User Validation
    user = userValidation(kakaoPayload)
    if (user == None):
        return errorView('잘못된 사용자 계정', '찾을 수 없는 사용자 계정 아이디입니다.')

    # User's Eatple Pass Validation
    eatplePassStatus = eatplePassValidation(user)
    if(eatplePassStatus != None):
        return eatplePassStatus

    order = orderValidation(kakaoPayload)
    if(order == None):
        return errorView('잘못된 주문 번호', '잘못된 주문 번호입니다.')

    store = storeValidation(kakaoPayload)
    menu = menuValidation(kakaoPayload)

    if(store == None or menu == None):
        return errorView('잘못된 주문 내역', '잘못된 주문 정보입니다.')

    # Order Record
    try:
        orderRecordSheet = OrderRecordSheet.objects.get(order=order)
    except OrderRecordSheet.DoesNotExist:
        orderRecordSheet = OrderRecordSheet()

    if (orderRecordSheet.timeoutValidation()):
        orderRecordSheet.recordUpdate(ORDER_RECORD_TIMEOUT)
        return kakaoView_TimeOut(KAKAO_BLOCK_USER_SET_PICKUP_TIME)

    # Order Log Record
    orderRecordSheet.user = user
    orderRecordSheet.order = order
    orderRecordSheet.recordUpdate(ORDER_RECORD_SET_PICKUP_TIEM)

    currentStock = menu.getCurrentStock()

    if(menu.max_stock <= menu.current_stock):
        KakaoInstantForm().Message(
            '이 메뉴는 이미 매진됬습니다.',
            '아쉽지만 다른 메뉴를 주문해주세요!',
            kakaoForm=kakaoForm
        )

        kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)

        return JsonResponse(kakaoForm.GetForm())

    isVacationDay = vacationTimeCheck()
    isClosedDay = weekendTimeCheck()

    if(isClosedDay or isVacationDay):
        KakaoInstantForm().Message(
            '📌  안내사항',
            '월요일 점심 주문은 일요일 오후 4시 30분부터 가능합니다.',
            kakaoForm=kakaoForm
        )

        kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)

        return JsonResponse(kakaoForm.GetForm())

    currentSellingTime = sellingTimeCheck()

    if (currentSellingTime == None):
        return errorView('잘못된 주문 시간', '정상적인 주문 시간대가 아닙니다.')
    elif currentSellingTime == SELLING_TIME_DINNER:
        KakaoInstantForm().Message(
            '오늘 점심은 이미 마감되었어요.',
            '내일 점심은 오늘 16:30부터 내일 10:30까지 주문하실 수 있어요.',
            kakaoForm=kakaoForm
        )

        kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)

        return JsonResponse(kakaoForm.GetForm())

    PICKUP_TIME_QUICKREPLIES_MAP = []

    pickupTimes = menu.pickup_time.filter(selling_time=currentSellingTime)

    order = orderValidation(kakaoPayload)

    isCafe = store.category.filter(name="카페").exists()
    if(isCafe):
        KakaoInstantForm().Message(
            '🛎  상시픽업이 가능한 점포입니다.',
            '오전 11:30 부터 오후 4:00까지 언제든 방문하여 메뉴를 픽업할 수 있습니다.',
            kakaoForm=kakaoForm
        )
    else:
        if(pickupTimes.count() < 2):
            KakaoInstantForm().Message(
                '❗ 픽업 시간이 제한된 점포입니다',
                '점주님의 요청으로 픽업 시간이 한 타임으로 제한된 점포입니다.',
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
            KAKAO_PARAM_STORE_ID: menu.store.store_id,
            KAKAO_PARAM_MENU_ID: menu.menu_id,
            KAKAO_PARAM_ORDER_ID: order.order_id,
            KAKAO_PARAM_PICKUP_TIME: orderTimeTable.GetLunchOrderPickupTimeStart().strftime('%H:%M'),
            KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_SET_PICKUP_TIME
        }

        kakaoForm.QuickReplies_Add(
            'block',
            "오전 11시 30분 ~ 오후 4시",
            KAKAO_EMOJI_LOADING,
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

    # User's Eatple Pass Validation
    eatplePassStatus = eatplePassValidation(user)
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
        orderRecordSheet.recordUpdate(ORDER_RECORD_TIMEOUT)
        return kakaoView_TimeOut(KAKAO_BLOCK_USER_SET_ORDER_SHEET)

    orderRecordSheet.user = user
    orderRecordSheet.order = order
    orderRecordSheet.recordUpdate(ORDER_RECORD_ORDERSHEET_CHECK)

    dataActionExtra = kakaoPayload.dataActionExtra
    dataActionExtra[KAKAO_PARAM_ORDER_ID] = order.order_id
    dataActionExtra[KAKAO_PARAM_PREV_BLOCK_ID] = KAKAO_BLOCK_USER_SET_ORDER_SHEET

    currentStock = order.menu.getCurrentStock()

    if(order.menu.max_stock <= order.menu.current_stock):
        KakaoInstantForm().Message(
            '이 메뉴는 이미 매진됬습니다.',
            '아쉽지만 다른 메뉴를 주문해주세요!',
            kakaoForm=kakaoForm
        )

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
            'nickname': '픽업 시간 : {pickup_time}'.format(pickup_time=dateByTimeZone(order.pickup_time).strftime(
                '%p %-I시 %-M분').replace('AM', '오전').replace('PM', '오후'),),
            'imageUrl': '{}{}'.format(HOST_URL, store.logoImgURL()),
        }

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

    if(ORDERING_DEBUG_MODE):
        server_url = 'http://localhost:3000'
    else:
        server_url = 'https://www.eatple.com'

    oneclick_url = 'kakaotalk://bizplugin?plugin_id={api_id}&oneclick_id={order_id}'.format(
        api_id=KAKAO_PAY_ONE_CLICK_API_ID,
        order_id=order.order_id
    )

    buttons = [
        {
            'action': 'osLink',
            'label': '원클릭 결제하기',
            'messageText': KAKAO_EMOJI_LOADING,
            'osLink': {
                'android': oneclick_url,
                'ios': oneclick_url,
            },
        },
        {
            'action': 'webLink',
            'label': '웹으로 결제하기',
            'messageText': KAKAO_EMOJI_LOADING,
            'extra': dataActionExtra,
            'webLinkUrl': '{server_url}/payment?merchant_uid={merchant_uid}'.format(
                server_url=server_url,
                merchant_uid=order.order_id,
            )
        },
    ]

    discount = 500

    kakaoForm.ComerceCard_Push(
        menu.description,
        menu.price + discount,
        discount,
        thumbnails,
        profile,
        buttons
    )

    kakaoForm.ComerceCard_Add()

    buttons = [
        {
            'action': 'block',
            'label': '결제 완료하기',
            'messageText': KAKAO_EMOJI_LOADING,
            'blockId': KAKAO_BLOCK_USER_SET_ORDER_SHEET,
            'extra': dataActionExtra,
        },
    ]

    KakaoInstantForm().Message(
        '결제 완료 후 아래 \'결제 완료하기\' 버튼을 눌러주세요.',
        buttons=buttons,
        kakaoForm=kakaoForm
    )

    GET_PICKUP_TIME_QUICKREPLIES_MAP = [
        {
            'action': 'message', 'label': '🏠  홈',
            'messageText': KAKAO_EMOJI_LOADING,
            'blockId': KAKAO_BLOCK_USER_HOME,
            'extra': {}
        },
    ]

    kakaoForm.QuickReplies_AddWithMap(GET_PICKUP_TIME_QUICKREPLIES_MAP)

    return JsonResponse(kakaoForm.GetForm())


def kakaoView_OrderPaymentCheck(kakaoPayload):
    kakaoForm = KakaoForm()

    QUICKREPLIES_MAP = [
        {
            'action': 'block',
            'label': '🏠  홈',
            'messageText': '🏠  홈',
            'blockId': KAKAO_BLOCK_USER_HOME,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_EDIT_PICKUP_TIME
            }
        },
    ]

    # Block Validation
    prev_block_id = prevBlockValidation(kakaoPayload)
    if(prev_block_id != KAKAO_BLOCK_USER_SET_ORDER_SHEET and prev_block_id != KAKAO_BLOCK_USER_SET_PICKUP_TIME):
        return errorView('잘못된 블럭 경로', '정상적이지 않은 경로거나, 오류가 발생했습니다.\n다시 주문해주세요!')

    # User Validation
    user = userValidation(kakaoPayload)
    if (user == None):
        return errorView('잘못된 블럭 경로', '정상적이지 않은 경로거나, 잘못된 계정입니다.')

    order = orderValidation(kakaoPayload)
    if(order == None):
        return errorView('결제 실패', '주문을 도중에 중단한 주문 번호 입니다.')
    else:
        order.orderStatusUpdate()

    store = storeValidation(kakaoPayload)
    menu = menuValidation(kakaoPayload)
    if(store == None or menu == None):
        return errorView('결제 실패', '주문을 도중에 중단한 주문 번호 입니다.')

    if(order.store != store or order.menu != menu):
        return kakaoView_OrderPayment(kakaoPayload)

    # Order Record
    try:
        orderRecordSheet = OrderRecordSheet.objects.get(order=order)
    except OrderRecordSheet.DoesNotExist:
        orderRecordSheet = OrderRecordSheet()

    if (orderRecordSheet.timeoutValidation()):
        orderRecordSheet.recordUpdate(ORDER_RECORD_TIMEOUT)
        return kakaoView_TimeOut(KAKAO_BLOCK_USER_SET_ORDER_SHEET)

    orderRecordSheet.user = user
    orderRecordSheet.order = order
    orderRecordSheet.recordUpdate(ORDER_RECORD_PAYMENT_CONFIRM)

    if(order.payment_status == EATPLE_ORDER_STATUS_CANCELLED):
        KakaoInstantForm().Message(
            '이 잇플 패스는 이미 취소된 잇플 패스입니다.',
            '다시 주문을 확인해주세요.',
            kakaoForm=kakaoForm
        )

        kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)

        return JsonResponse(kakaoForm.GetForm())

    dataActionExtra = kakaoPayload.dataActionExtra
    dataActionExtra[KAKAO_PARAM_ORDER_ID] = order.order_id
    dataActionExtra[KAKAO_PARAM_PREV_BLOCK_ID] = KAKAO_BLOCK_USER_SET_ORDER_SHEET

    if(order.payment_status == EATPLE_ORDER_STATUS_PAID):
        return kakaoView_EatplePassIssuance(kakaoPayload)
    else:
        if(ORDERING_DEBUG_MODE):
            server_url = 'http://localhost:3000'
        else:
            server_url = 'https://www.eatple.com'

        oneclick_url = 'kakaotalk://bizplugin?plugin_id={api_id}&oneclick_id={order_id}'.format(
            api_id=KAKAO_PAY_ONE_CLICK_API_ID,
            order_id=order.order_id
        )

        thumbnail = {
            'imageUrl': ''.format(),
            'fixedRatio': 'true',
            'width': 800,
            'height': 800,
        }

        buttons = [
            {
                'action': 'osLink',
                'label': '원클릭 결제하기',
                'messageText': KAKAO_EMOJI_LOADING,
                'osLink': {
                    'android': oneclick_url,
                    'ios': oneclick_url,
                },
            },
            {
                'action': 'webLink',
                'label': '웹으로 결제하기',
                'messageText': KAKAO_EMOJI_LOADING,
                'extra': dataActionExtra,
                'webLinkUrl': '{server_url}/payment?merchant_uid={merchant_uid}'.format(
                    server_url=server_url,
                    merchant_uid=order.order_id,
                )
            },
        ]

        KakaoInstantForm().Message(
            '아직 결제가 완료되지 않았어요!',
            '{menu} - {price}원'.format(menu=menu.name,
                                       price=order.totalPrice),
            buttons=buttons,
            thumbnail=thumbnail,
            kakaoForm=kakaoForm
        )

        buttons = {
            'action': 'block',
            'label': '결제 완료하기',
            'messageText': KAKAO_EMOJI_LOADING,
            'blockId': KAKAO_BLOCK_USER_SET_ORDER_SHEET,
            'extra': dataActionExtra,
        },

        KakaoInstantForm().Message(
            '결제 완료 후 아래 \'결제 완료하기\' 버튼을 눌러주세요.',
            buttons=buttons,
            kakaoForm=kakaoForm
        )

        kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)

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
            return errorView('주문 상태 확인', '정상적이지 않은 경로거나 이미 발급이 완료되었어요!')
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

        if (orderRecordSheet.timeoutValidation()):
            orderRecordSheet.recordUpdate(ORDER_RECORD_TIMEOUT)
            return kakaoView_TimeOut(KAKAO_BLOCK_USER_SET_ORDER_SHEET)

        orderRecordSheet.user = user
        orderRecordSheet.order = order
        orderRecordSheet.paid = True
        orderRecordSheet.recordUpdate(ORDER_RECORD_PAYMENT_COMPLETED)

        dataActionExtra = kakaoPayload.dataActionExtra
        dataActionExtra[KAKAO_PARAM_ORDER_ID] = order.order_id
        dataActionExtra[KAKAO_PARAM_PREV_BLOCK_ID] = KAKAO_BLOCK_USER_SET_ORDER_SHEET

        order.payment_date = dateNowByTimeZone()
        order.save()

        KakaoInstantForm().Message(
            '잇플패스 발급이 완료되었습니다.',
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
def GET_Menu(request):
    EatplusSkillLog('GET_Menu')

    kakaoPayload = KakaoPayLoad(request)

    # User Validation
    user = userValidation(kakaoPayload)
    if (user == None):
        return GET_UserHome(request)

    # User Case
    addressMap = user.location.address.split()
    if(addressMap[0] == "서울"):
        return kakaoView_MenuListup(kakaoPayload)
    else:
        return kakaoView_MenuListupWithAreaOut(kakaoPayload)


@csrf_exempt
def SET_PickupTime(request):
    EatplusSkillLog('SET_PickupTime')

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
    EatplusSkillLog('SET_OrderSheet')

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
