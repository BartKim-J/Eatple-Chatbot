# View-System
from eatple_app.views_system.include import *
from eatple_app.views_system.debugger import *

from eatple_app.views import GET_UserHome, GET_EatplePass
from eatple_app.views_user.b2b.orderFlow import GET_B2B_Store, GET_B2B_Menu, SET_B2B_PickupTime, SET_B2B_OrderSheet

from eatple_app.apis.pixel.pixel_logger import Pixel_viewStore, Pixel_viewMenu, Pixel_setPickupTime, Pixel_orderSheet

# STATIC CONFIG
MENU_LIST_LENGTH = 20
DEFAULT_DISTANCE_CONDITION = 800
DEFAULT_AREA_IN_FLAG = True
DEFAULT_AREA_CODE = None

FRIEND_DISCOUNT = 2000
PERCENT_DISCOUNT = 0

DELIVERY_FEE = 500

FAST_FIVE_FLOOR = [3, 4, 5, 9, 11, 12, 13]

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


def isServiceArea(user):
    addressMap = user.location.address.split()

    for code, area in SERVICE_AREAS.items():
        if(addressMap[2].find(area['name']) != -1):
            return True
        else:
            pass

    return False


def applyDiscount(user, menu):
    addressMap = user.location.address.split()

    discount = 0

    if(PERCENT_DISCOUNT > 0 and addressMap[2].find('신사') != -1):
        eatple_discount = menu.price_origin - menu.price
        percent_discount = (menu.price_origin / 2)

        discount = percent_discount
    elif(user.friend_discount_count > 0):
        discount = FRIEND_DISCOUNT + \
            (menu.price_origin - menu.price)
    else:
        discount = menu.price_origin - menu.price

    return discount

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

    if(sellingTime == None):
        if (lunchPurchaed or dinnerPurchaced):
            return GET_EatplePass(kakaoPayload.request)
    else:
        if (lunchPurchaed and sellingTime == SELLING_TIME_LUNCH):
            return GET_EatplePass(kakaoPayload.request)

        if (dinnerPurchaced and sellingTime == SELLING_TIME_DINNER):
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


def kakaoView_StoreListup(kakaoPayload):
    kakaoForm = KakaoForm()

    QUICKREPLIES_MAP = [
        {
            'action': 'block',
            'label': '위치 변경',
            'messageText': KAKAO_EMOJI_LOADING,
            'blockId': KAKAO_BLOCK_USER_EDIT_LOCATION_AT_STORE,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_GET_STORE
            }
        },
        {
            'action': 'block',
            'label': '🏠  홈',
            'messageText': '🏠  홈',
            'blockId': KAKAO_BLOCK_USER_HOME,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_GET_STORE
            }
        },
    ]

    # User Validation
    user = userValidation(kakaoPayload)
    if (user == None):
        return errorView('잘못된 사용자 계정', '찾을 수 없는 사용자 계정 아이디입니다.')

    # @BETA Dinner Beta
    sellingTime = sellingTimeValidation(kakaoPayload)
    currentSellingTime = sellingTimeCheck()

    # User's Eatple Pass Validation
    eatplePassStatus = isPurchase(user, sellingTime, kakaoPayload)
    if(eatplePassStatus != None):
        return eatplePassStatus

    if(sellingTime == None):
        sellingTime = sellingTimeCheck(True)

    order = orderValidation(kakaoPayload)

    if (order != None):
        order.store = None
        order.menu = None
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
            delivery_fee=0,
            discount=0,
            count=1,
            type=ORDER_TYPE_NORMAL
        )
        order.save()

        # Order Log Record Init
        orderRecordSheet = OrderRecordSheet()
        orderRecordSheet.recordUpdate(user, order, ORDER_RECORD_GET_STORE)

    distance_condition = DEFAULT_DISTANCE_CONDITION
    area_in_flag = DEFAULT_AREA_IN_FLAG
    area_code = DEFAULT_AREA_CODE
    '''
    try:
        distance_condition = kakaoPayload.dataActionExtra['distance_condition']
        area_in_flag = kakaoPayload.dataActionExtra['area_in_flag']
        area_code = kakaoPayload.dataActionExtra['area']

        QUICKREPLIES_MAP.insert(0, {
            'action': 'block',
            'label': '내 지역',
            'messageText': KAKAO_EMOJI_LOADING,
            'blockId': KAKAO_BLOCK_USER_GET_STORE,
            'extra': {
                KAKAO_PARAM_SELLING_TIME: sellingTime,
                KAKAO_PARAM_ORDER_ID: order.order_id,
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_GET_STORE,
                'distance_condition': DEFAULT_DISTANCE_CONDITION,
                'area_in_flag': True,
            }
        })
    except:
        pass

    for code, area in SERVICE_AREAS.items():
        if(area_code != code):
            QUICKREPLIES_MAP.insert(0, {
                'action': 'block',
                'label': '{}역'.format(area['name']),
                'messageText': KAKAO_EMOJI_LOADING,
                'blockId': KAKAO_BLOCK_USER_GET_STORE,
                'extra': {
                    KAKAO_PARAM_SELLING_TIME: sellingTime,
                    KAKAO_PARAM_ORDER_ID: order.order_id,
                    KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_GET_STORE,
                    'distance_condition': DEFAULT_DISTANCE_CONDITION,
                    'area_in_flag': False,
                    'area': code
                }
            })

    '''

    storeList = Store.objects.annotate(
        distance=Distance(F('place__point'),
                          user.location.point) * 100 * 1000
    ).filter(
        (
            Q(type=STORE_TYPE_B2B_AND_NORMAL) |
            Q(type=STORE_TYPE_NORMAL)
        ) &
        (
            Q(status=OC_OPEN) |
            Q(status=STORE_OC_VACATION)
        )
    ).order_by(F'distance')

    # @PROMOTION
    addressMap = user.location.address.split()

    if(area_in_flag):
        storeList = storeList.filter(Q(distance__lte=distance_condition))
    else:
        storeList = storeList.annotate(
            distance=Distance(
                F('place__point'),
                Point(y=SERVICE_AREAS[area_code]['y'], x=SERVICE_AREAS[area_code]['x'], srid=4326)) * 100 * 1000,
        )

        storeList = storeList.filter(Q(distance__lte=distance_condition))

    if storeList:
        if(user.friend_discount_count > 0):
            KakaoInstantForm().Message(
                '🏷  할인 쿠폰이 자동으로 적용됩니다.',
                '할인 쿠폰을 {}회 사용할 수 있습니다.'.format(
                    user.friend_discount_count
                ),
                kakaoForm=kakaoForm
            )
        else:
            KakaoInstantForm().Message(
                '\'메뉴판 보기\'에서 메뉴를 확인하세요',
                '',
                kakaoForm=kakaoForm
            )

        # HEADER
        if(SELLING_TIME_LUNCH == sellingTime):
            # LUNCH HEADER
            lunchHomeImg = '{}{}'.format(HOST_URL, EATPLE_HEADER_LUNCH_IMG)

            thumbnail = {
                'imageUrl': lunchHomeImg,
                'fixedRatio': 'true',
                'width': 800,
                'height': 800,
            }

            kakaoForm.BasicCard_Push(
                '점심 주문 가능/취소 시간',
                '픽업 전날 오후 9시부터 오전 11시까지',
                thumbnail,
                [],
            )

            QUICKREPLIES_MAP.insert(1, {
                'action': 'block',
                'label': '저녁 메뉴 보러가기',
                'messageText': KAKAO_EMOJI_LOADING,
                'blockId': KAKAO_BLOCK_USER_GET_STORE,
                'extra': {
                    KAKAO_PARAM_SELLING_TIME: SELLING_TIME_DINNER,
                    KAKAO_PARAM_ORDER_ID: order.order_id,
                    KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_GET_STORE,
                    'distance_condition': DEFAULT_DISTANCE_CONDITION,
                    'area_in_flag': True,
                }
            })

            if((area_in_flag and addressMap[2] == '신사동') or (area_code == 'sinsa')):
                thumbnail = {
                    'imageUrl': '{}{}'.format(HOST_URL, EATPLE_MENU_PICKUP_ZONE_FF_IMG),
                    'fixedRatio': 'True',
                    'width': 800,
                    'height': 800,
                }

                buttons = [
                    {
                        'action': 'block',
                        'label': '📋 픽업존 주문하기',
                        'messageText': KAKAO_EMOJI_LOADING,
                        'blockId': KAKAO_BLOCK_USER_GET_MENU,
                        'extra': {
                            KAKAO_PARAM_SELLING_TIME: sellingTime,
                            KAKAO_PARAM_ORDER_ID: order.order_id,
                            KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_GET_STORE,
                            'pickupZoneStore': True,
                        }
                    },
                ]

                kakaoForm.BasicCard_Push(
                    '🔥  픽업존 시즌 2  🔥',
                    '픽업존 서비스는 이용료가 추가됩니다.',
                    thumbnail,
                    buttons
                )

        elif(SELLING_TIME_DINNER == sellingTime):
            # DINNER HEADER
            dinnerHeaderImg = '{}{}'.format(HOST_URL, EATPLE_HEADER_DINNER_IMG)

            thumbnail = {
                'imageUrl': dinnerHeaderImg,
                'fixedRatio': 'true',
                'width': 800,
                'height': 800,
            }

            kakaoForm.BasicCard_Push(
                '저녁 주문 가능/취소 시간',
                '픽업 당일 오후 2시부터 오후 6시까지',
                thumbnail,
                [],
            )

            QUICKREPLIES_MAP.insert(1, {
                'action': 'block',
                'label': '점심 메뉴 보러가기',
                'messageText': KAKAO_EMOJI_LOADING,
                'blockId': KAKAO_BLOCK_USER_GET_STORE,
                'extra': {
                    KAKAO_PARAM_SELLING_TIME: SELLING_TIME_LUNCH,
                    KAKAO_PARAM_ORDER_ID: order.order_id,
                    KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_GET_STORE,
                    'distance_condition': DEFAULT_DISTANCE_CONDITION,
                    'area_in_flag': True,
                }
            })
        else:
            pass

        onDisplayStore = 0
        # Menu Carousel Card Add
        for store in storeList:
            menu = Menu.objects.filter(
                Q(store=store) &
                ~Q(tag__name__contains='픽업존') &
                Q(selling_time=sellingTime) &
                (
                    Q(type=MENU_TYPE_B2B_AND_NORMAL) |
                    Q(type=MENU_TYPE_NORMAL)
                ) &
                Q(status=OC_OPEN)
            ).first()

            if(menu):
                onDisplayStore += 1
                currentStock = menu.getCurrentStock()

                distance = store.distance
                walkTime = round((distance / 100) * 1.2)

                if(distance <= distance_condition):
                    if(area_in_flag):
                        walkTime = '약 도보 {} 분'.format(walkTime)
                    else:
                        walkTime = '약 도보 {} 분( {}역 )'.format(
                            walkTime, SERVICE_AREAS[area_code]['name'])
                else:
                    walkTime = '1 ㎞ 이상'

                if(store.coverImgURL().find('default') == -1):
                    thumbnail = {
                        'imageUrl': '{}{}'.format(HOST_URL, store.coverImgURL()),
                        'fixedRatio': 'True',
                        'width': 800,
                        'height': 800,
                    }
                else:
                    thumbnail = {
                        'imageUrl': '{}{}'.format(HOST_URL, menu.imgURL()),
                        'fixedRatio': 'False',
                        'width': 800,
                        'height': 800,
                    }

                kakaoMapUrl = 'https://map.kakao.com/link/map/{name},{place}'.format(
                    name=menu.store.name,
                    place=menu.store.place
                )

                buttons = [
                    {
                        'action': 'webLink',
                        'label': '📍  매장 위치',
                        'webLinkUrl': kakaoMapUrl,
                    },
                    {
                        'action': 'block',
                        'label': '📋  메뉴판 보기',
                        'messageText': KAKAO_EMOJI_LOADING,
                        'blockId': KAKAO_BLOCK_USER_GET_MENU,
                        'extra': {
                            KAKAO_PARAM_SELLING_TIME: sellingTime,
                            KAKAO_PARAM_STORE_ID: store.store_id,
                            KAKAO_PARAM_ORDER_ID: order.order_id,
                            KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_GET_STORE
                        }
                    },
                ]

                pickupTimeList = '⏱️  매장 방문 픽업가능 시간\n - '

                for pickup_time in menu.pickup_time.all():
                    if(menu.pickup_time.first() != pickup_time):
                        pickupTimeList += ', '

                        pickupTimeList += pickup_time.time.strftime('%-I:%M')
                    else:
                        pickupTimeList += pickup_time.time.strftime(
                            '%p %-I:%M').replace('AM', '오전').replace('PM', '오후')

                KakaoInstantForm().StoreList(
                    store,
                    walkTime,
                    pickupTimeList,
                    thumbnail,
                    buttons,
                    kakaoForm
                )
            else:
                # Store have don't exist menu
                pass

        if(onDisplayStore < 1):
            kakaoForm.Reset()

            kakaoForm.BasicCard_Push(
                '근처에 제휴된 {} 매장이 없습니다..'.format(
                    dict(SELLING_TIME_CATEGORY)[sellingTime]),
                '빠른 시일안에 이 지역 매장을 늘려볼게요.',
                {},
                []
            )

        kakaoForm.BasicCard_Add()

        if(weekendTimeCheck(sellingTime)):
            KakaoInstantForm().Message(
                '🔴  주문 가능 시간이 아닙니다.',
                '',
                kakaoForm=kakaoForm
            )
        elif(currentSellingTime == sellingTime):
            if(sellingTime == SELLING_TIME_LUNCH):
                subtext = '픽업 전날 오후 9시부터 오전 11시까지'
            else:
                subtext = '픽업 당일 오후 2시부터 오후 6시까지'

            KakaoInstantForm().Message(
                '🟢  주문 가능 시간입니다.',
                subtext,
                kakaoForm=kakaoForm
            )
        else:
            if(sellingTimeCheck() == None):
                currentSellingTime = sellingTimeCheck(True)

                if (currentSellingTime == None):
                    return errorView('잘못된 주문 시간', '정상적인 주문 시간대가 아닙니다.')

                if (currentSellingTime == SELLING_TIME_DINNER):
                    if (sellingTime == SELLING_TIME_DINNER):
                        KakaoInstantForm().Message(
                            '🔴  주문은 오후 2시부터 가능합니다.',
                            '',
                            kakaoForm=kakaoForm
                        )
                    else:
                        KakaoInstantForm().Message(
                            '🔴  금일 점심 주문이 마감되었습니다.',
                            '',
                            kakaoForm=kakaoForm
                        )

                elif (currentSellingTime == SELLING_TIME_LUNCH):
                    if (sellingTime == SELLING_TIME_DINNER):
                        KakaoInstantForm().Message(
                            '🔴  금일 저녁 주문이 마감되었습니다.',
                            '',
                            kakaoForm=kakaoForm
                        )
                    else:
                        KakaoInstantForm().Message(
                            '🔴  주문은 오후 9시부터 가능합니다.',
                            '',
                            kakaoForm=kakaoForm
                        )
            else:
                if (sellingTime == SELLING_TIME_DINNER):
                    KakaoInstantForm().Message(
                        '🔴  주문 가능 시간이 아닙니다.',
                        '',
                        kakaoForm=kakaoForm
                    )
                elif (sellingTime == SELLING_TIME_LUNCH):
                    KakaoInstantForm().Message(
                        '🔴  주문 가능 시간이 아닙니다.',
                        '',
                        kakaoForm=kakaoForm
                    )

    else:
        kakaoForm.BasicCard_Push(
            '근처에 제휴된 매장이 없습니다..',
            '빠른 시일안에 이 지역 매장을 늘려볼게요.',
            {},
            []
        )

        kakaoForm.BasicCard_Add()

    kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)

    return JsonResponse(kakaoForm.GetForm())


def kakaoView_PickupZone_MenuListup(kakaoPayload):
    kakaoForm = KakaoForm()

    # User Validation
    user = userValidation(kakaoPayload)
    if (user == None):
        return errorView('잘못된 사용자 계정', '찾을 수 없는 사용자 계정 아이디입니다.')

    order = orderValidation(kakaoPayload)
    if (order != None):
        order.store = None
        order.menu = None
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
            delivery_fee=0,
            discount=0,
            count=1,
            type=ORDER_TYPE_NORMAL
        )
        order.save()

    # @BETA Dinner Beta
    sellingTime = sellingTimeValidation(kakaoPayload)

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
        {
            'action': 'block',
            'label': '뒤로가기',
            'messageText': KAKAO_EMOJI_LOADING,
            'blockId': KAKAO_BLOCK_USER_GET_STORE,
            'extra': {
                KAKAO_PARAM_SELLING_TIME: sellingTime,
                KAKAO_PARAM_ORDER_ID: order.order_id,
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_GET_MENU
            }
        },
    ]

    sellingOutList = []

    menuList = Menu.objects.filter(
        Q(tag__name__contains='픽업존') &
        Q(selling_time=SELLING_TIME_LUNCH) &
        Q(status=OC_OPEN) &
        (
            Q(store__status=OC_OPEN) |
            Q(store__status=STORE_OC_VACATION)
        ) &
        (
            Q(store__type=STORE_TYPE_B2B_AND_NORMAL) |
            Q(store__type=STORE_TYPE_NORMAL)
        ) &
        (
            Q(type=MENU_TYPE_B2B_AND_NORMAL) |
            Q(type=MENU_TYPE_NORMAL)
        )
    ).order_by(F'-index', F'price', F'name')

    if menuList:
        KakaoInstantForm().Message(
            '픽업존 서비스는 이용료가 추가됩니다.',
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
                    'width': 800,
                    'height': 800,
                }

                kakaoMapUrl = 'https://map.kakao.com/link/map/{name},{place}'.format(
                    name=menu.store.name,
                    place=menu.store.place
                )

                buttons = [
                    {
                        'action': 'block',
                        'label': '주문하기',
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

                discount = applyDiscount(user, menu)

                KakaoInstantForm().MenuList(
                    menu,
                    '픽업존',
                    discount,
                    thumbnail,
                    buttons,
                    kakaoForm
                )

            else:  # selling out
                sellingOutList.extend(list(Menu.objects.filter(id=menu.id)))

        for menu in sellingOutList:
            kakaoMapUrl = 'https://map.kakao.com/link/map/{name},{place}'.format(
                name=menu.store.name,
                place=menu.store.place
            )

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

            discount = applyDiscount(user, menu)

            KakaoInstantForm().MenuList(
                menu,
                '매진',
                discount,
                thumbnail,
                buttons,
                kakaoForm
            )

        kakaoForm.ComerceCard_Add(None)

        KakaoInstantForm().Message(
            '픽업 시간은 오후 12시 10분입니다.',
            '',
            kakaoForm=kakaoForm
        )

    else:
        KakaoInstantForm().Message(
            '당일 픽업존 이벤트는 종료되었습니다.',
            '내일 픽업존 메뉴를 기대해주세요.',
            kakaoForm=kakaoForm
        )

    kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)

    return JsonResponse(kakaoForm.GetForm())


def kakaoView_MenuListup(kakaoPayload):
    kakaoForm = KakaoForm()

    # User Validation
    user = userValidation(kakaoPayload)
    if (user == None):
        return errorView('잘못된 사용자 계정', '찾을 수 없는 사용자 계정 아이디입니다.')

    # @PROTOMOTION
    try:
        isPickupZoneStore = kakaoPayload.dataActionExtra['pickupZoneStore']
        if(isPickupZoneStore):
            return kakaoView_PickupZone_MenuListup(kakaoPayload)
        else:
            pass
    except Exception as ex:
        pass

    store = storeValidation(kakaoPayload)
    if (store == None):
        return errorView('잘못된 주문 경로', '처음부터 다시 주문해주세요.')

    order = orderValidation(kakaoPayload)
    if(order == None):
        return errorView('잘못된 주문 번호', '잘못된 주문 번호입니다.')

    # @BETA Dinner Beta
    sellingTime = sellingTimeValidation(kakaoPayload)

    # User's Eatple Pass Validation
    eatplePassStatus = isPurchase(user, sellingTime, kakaoPayload)
    if(eatplePassStatus != None):
        return eatplePassStatus

    # Order Log Record
    order.store = store
    order.save()

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
        orderRecordSheet.recordUpdate(user, order, ORDER_RECORD_GET_MENU)

    distance_condition = DEFAULT_DISTANCE_CONDITION
    area_in_flag = DEFAULT_AREA_IN_FLAG
    area_code = DEFAULT_AREA_CODE

    menuList = Menu.objects.annotate(
        distance=Distance(F('store__place__point'),
                          user.location.point) * 100 * 1000,
    ).filter(
        Q(store=store) &
        ~Q(tag__name__contains='픽업존') &
        Q(selling_time=sellingTime) &
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
    ).order_by(F'-index', F'price', F'name')

    sellingOutList = []

    if menuList:
        if(user.friend_discount_count > 0):
            KakaoInstantForm().Message(
                '🏷  할인 쿠폰이 적용되었습니다.',
                '할인 금액 : 2000원 + 잇플 할인',
                kakaoForm=kakaoForm
            )
        # Menu Carousel Card Add
        for menu in menuList:
            currentStock = menu.getCurrentStock()

            if(menu.max_stock > menu.current_stock):
                distance = menu.distance
                walkTime = round((distance / 100) * 1.2)

                if(distance <= distance_condition):
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
                    'width': 800,
                    'height': 800,
                }

                kakaoMapUrl = 'https://map.kakao.com/link/map/{name},{place}'.format(
                    name=menu.store.name,
                    place=menu.store.place
                )

                buttons = [
                    {
                        'action': 'block',
                        'label': '주문하기',
                        'messageText': KAKAO_EMOJI_LOADING,
                        'blockId': KAKAO_BLOCK_USER_SET_PICKUP_TIME,
                        'extra': {
                            KAKAO_PARAM_SELLING_TIME: sellingTime,
                            KAKAO_PARAM_STORE_ID: store.store_id,
                            KAKAO_PARAM_MENU_ID: menu.menu_id,
                            KAKAO_PARAM_ORDER_ID: order.order_id,
                            KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_GET_MENU
                        }
                    },
                ]

                discount = applyDiscount(user, menu)

                KakaoInstantForm().MenuList(
                    menu,
                    walkTime,
                    discount,
                    thumbnail,
                    buttons,
                    kakaoForm
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

                discount = applyDiscount(user, menu)

                KakaoInstantForm().MenuList(
                    menu,
                    '휴무중',
                    discount,
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

                discount = applyDiscount(user, menu)

                KakaoInstantForm().MenuList(
                    menu,
                    status,
                    discount,
                    thumbnail,
                    buttons,
                    kakaoForm
                )

        kakaoForm.ComerceCard_Add(None)

    else:
        KakaoInstantForm().Message(
            '판매중인 메뉴가 없습니다.',
            '빠른 시일안에 이 지역 매장을 늘려볼게요.',
            kakaoForm=kakaoForm
        )

    kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)

    return JsonResponse(kakaoForm.GetForm())


def kakaoView_MenuListupWithAreaOut(kakaoPayload):
    kakaoForm = KakaoForm()

    QUICKREPLIES_MAP = [
        {
            'action': 'block',
            'label': '위치 변경',
            'messageText': KAKAO_EMOJI_LOADING,
            'blockId': KAKAO_BLOCK_USER_EDIT_LOCATION_AT_STORE,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_GET_STORE
            }
        },
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

    menuList = Menu.objects.annotate(
        distance=Distance(F('store__place__point'),
                          user.location.point) * 100 * 1000,
    ).filter(
        ~Q(tag__name__contains='픽업존') &
        Q(selling_time=SELLING_TIME_LUNCH) &
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
    ).order_by(F'distance', F'price')

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

                discount = applyDiscount(user, menu)

                KakaoInstantForm().MenuList(
                    menu,
                    '서비스 지역 아님',
                    discount,
                    thumbnail,
                    buttons,
                    kakaoForm
                )

        kakaoForm.ComerceCard_Add()

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
            if (sellingTime == SELLING_TIME_DINNER):
                KakaoInstantForm().Message(
                    '🔴  현재는 주문 가능 시간이 아닙니다.',
                    '저녁(당일) - 오늘 오후 2시부터\n점심(당일) - 마감되었습니다.',
                    kakaoForm=kakaoForm
                )
            else:
                KakaoInstantForm().Message(
                    '🔴  현재는 주문 가능 시간이 아닙니다.',
                    '점심(당일) - 마감되었습니다.\n저녁(당일) - 오늘 오후 2시부터',
                    kakaoForm=kakaoForm
                )

            kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)

            return JsonResponse(kakaoForm.GetForm())

        elif (currentSellingTime == SELLING_TIME_LUNCH):
            if (sellingTime == SELLING_TIME_DINNER):
                KakaoInstantForm().Message(
                    '🔴  현재는 주문 가능 시간이 아닙니다.',
                    '저녁(당일) - 마감되었습니다.\n점심(내일) - 오늘 오후 9시부터',
                    kakaoForm=kakaoForm
                )
            else:
                KakaoInstantForm().Message(
                    '🔴  현재는 주문 가능 시간이 아닙니다.',
                    '점심(내일) - 오늘 오후 9시부터\n저녁(당일) - 마감되었습니다.',
                    kakaoForm=kakaoForm
                )

            kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)

            return JsonResponse(kakaoForm.GetForm())
    else:
        currentSellingTime = sellingTimeCheck()

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

        if(sellingTime != currentSellingTime):
            QUICKREPLIES_MAP.append(
                {
                    'action': 'block',
                    'label': '{} 주문하기'.format(dict(SELLING_TIME_CATEGORY)[currentSellingTime]),
                    'messageText': KAKAO_EMOJI_LOADING,
                    'blockId': KAKAO_BLOCK_USER_GET_STORE,
                    'extra': {
                        KAKAO_PARAM_SELLING_TIME: currentSellingTime,
                        KAKAO_PARAM_STORE_ID: store.store_id,
                        KAKAO_PARAM_ORDER_ID: order.order_id,
                        KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_GET_MENU
                    }
                },
            )
            if (sellingTime == SELLING_TIME_DINNER):
                if(dateNowByTimeZone().hour <= 5):
                    KakaoInstantForm().Message(
                        '🔴  오늘 저녁은 아직 준비중입니다.',
                        '저녁(당일) - 마감되었습니다.\n점심(내일) - 주문 받는 중',
                        kakaoForm=kakaoForm
                    )
                else:
                    KakaoInstantForm().Message(
                        '🔴  오늘 저녁은 이미 마감됬어요.',
                        '저녁(당일) - 마감되었습니다.\n점심(내일) - 주문 받는 중',
                        kakaoForm=kakaoForm
                    )

                kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)

                return JsonResponse(kakaoForm.GetForm())
            elif (sellingTime == SELLING_TIME_LUNCH):
                KakaoInstantForm().Message(
                    '🔴  오늘 점심은 이미 마감되었어요.',
                    '점심(내일) - 오늘 오후 9시부터\n저녁(당일) - 주문 받는 중.',
                    kakaoForm=kakaoForm
                )

                kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)

                return JsonResponse(kakaoForm.GetForm())

    PICKUP_TIME_QUICKREPLIES_MAP = []

    pickupTimes = menu.pickup_time.filter(selling_time=currentSellingTime)

    order = orderValidation(kakaoPayload)

    isPickupZone = menu.tag.filter(name='픽업존').exists()

    isCafe = store.category.filter(name='카페').exists()
    if(isCafe):
        KakaoInstantForm().Message(
            '🛎  상시픽업이 가능한 매장입니다.',
            '오전 11시 30분 부터 오후 2시 까지 언제든 방문하여 메뉴를 픽업할 수 있습니다.',
            kakaoForm=kakaoForm
        )
    elif(isPickupZone):
        pass
    else:
        if(pickupTimes.count() < 2):
            KakaoInstantForm().Message(
                '❗ 픽업 시간이 제한된 매장입니다',
                '점주님의 요청으로 픽업 시간이 한 타임으로 제한된 매장입니다.',
                kakaoForm=kakaoForm
            )

    if(isPickupZone):
        pickupZone_PickupTime = '12:10'

        KakaoInstantForm().Message(
            '픽업 할 장소를 선택해주세요.',
            kakaoForm=kakaoForm
        )

        delivery_address = user.get_delivery_address()

        if(delivery_address > 100):
            delivery_floor = int(delivery_address / 100)
        else:
            delivery_floor = int(delivery_address % 100)

        isFastFiveFloor = False
        for floor in FAST_FIVE_FLOOR:
            if(delivery_floor == floor):
                isFastFiveFloor = True
                break

        if(isFastFiveFloor):
            kakaoForm.QuickReplies_Add(
                'block',
                '3층 픽업존',
                KAKAO_EMOJI_LOADING,
                KAKAO_BLOCK_USER_SET_ORDER_SHEET,
                {
                    KAKAO_PARAM_SELLING_TIME: sellingTime,
                    KAKAO_PARAM_STORE_ID: menu.store.store_id,
                    KAKAO_PARAM_MENU_ID: menu.menu_id,
                    KAKAO_PARAM_ORDER_ID: order.order_id,
                    KAKAO_PARAM_PICKUP_TIME: pickupZone_PickupTime,
                    KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_SET_PICKUP_TIME,
                    KAKAO_PARAM_DELIVERY_ADDRESS: 0,
                }
            )
        else:
            pass

        if(delivery_address == None):
            kakaoForm.QuickReplies_Add(
                'block',
                '사무실 등록',
                KAKAO_EMOJI_LOADING,
                KAKAO_BLOCK_USER_DELIVERY_ADDRESS_SUBMIT,
                {
                    KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_SET_PICKUP_TIME,
                }
            )
        else:
            if(delivery_address > 14):
                locationStr = '호'
            else:
                locationStr = '층'

            kakaoForm.QuickReplies_Add(
                'block',
                '내 사무실({}{})'.format(
                    delivery_address,
                    locationStr
                ),
                KAKAO_EMOJI_LOADING,
                KAKAO_BLOCK_USER_SET_ORDER_SHEET,
                {
                    KAKAO_PARAM_SELLING_TIME: sellingTime,
                    KAKAO_PARAM_STORE_ID: menu.store.store_id,
                    KAKAO_PARAM_MENU_ID: menu.menu_id,
                    KAKAO_PARAM_ORDER_ID: order.order_id,
                    KAKAO_PARAM_PICKUP_TIME: pickupZone_PickupTime,
                    KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_SET_PICKUP_TIME,
                    KAKAO_PARAM_DELIVERY_ADDRESS: delivery_address,
                }
            )
            kakaoForm.QuickReplies_Add(
                'block',
                '사무실 변경',
                KAKAO_EMOJI_LOADING,
                KAKAO_BLOCK_USER_DELIVERY_ADDRESS_SUBMIT,
                {}
            )
    else:
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

    isPickupZone = menu.tag.filter(name='픽업존').exists()
    if(isPickupZone):
        delivery_address = deliveryAddressValidation(kakaoPayload)
        if(delivery_address == None):
            return errorView('잘못된 주문 내역', '잘못된 주문 정보입니다.')
    else:
        delivery_address = 0
        pass

    order = orderValidation(kakaoPayload)
    if(order == None):
        return errorView('잘못된 주문 번호', '잘못된 주문 번호입니다.')
    else:
        discount = applyDiscount(user, menu)
        isPickupZone = menu.tag.filter(name='픽업존').exists()

        # Delivery Fee
        if(isPickupZone):
            delivery_fee = DELIVERY_FEE
        else:
            delivery_fee = 0

        order.user = user
        order.menu = menu
        order.store = store
        order.pickup_time = order.pickupTimeToDateTime(pickup_time)
        order.totalPrice = menu.price_origin - discount + delivery_fee
        order.delivery_fee = delivery_fee
        if(delivery_address == 0):
            order.delivery_address = 0
            order.is_delivery = False
        else:
            order.delivery_address = delivery_address
            order.is_delivery = True

        order.discount = discount - (menu.price_origin - menu.price)
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

    KakaoInstantForm().Message(
        '💳  결제 준비가 완료되었습니다.',
        '결제 금액을 확인하시고 결제해주세요.',
        kakaoForm=kakaoForm
    )

    # Menu Carousel Card Add
    thumbnails = [
        {
            'imageUrl': None,
            'fixedRatio': 'true',
            'width': 800,
            'height': 800,
        }
    ]

    if(isPickupZone):
        description = '주문금액 {amount}원 + 이용료 {delivery_fee}원'.format(
            amount=(order.totalPrice - order.delivery_fee),
            delivery_fee=order.delivery_fee,
        )
    else:
        isCafe = store.category.filter(name='카페').exists()
        if(isCafe):
            description = '픽업 시간 : {pickup_time}'.format(pickup_time=order.pickup_time.strftime(
                '%-m월 %-d일 오전 11시 30분 ~ 오후 2시'))
        else:
            description = '픽업 시간 : {pickup_time}'.format(pickup_time=order.pickup_time.strftime(
                '%p %-I시 %-M분').replace('AM', '오전').replace('PM', '오후'))

    profile = {
        'nickname': '{} - {}'.format(menu.store.name, menu.name),
        'imageUrl': '{}{}'.format(HOST_URL, store.logoImgURL()),
    }

    host_url = 'https://www.eatple.com'

    if(False and settings.SETTING_ID == 'DEBUG'):
        oneclick_url = 'kakaotalk://bizplugin?plugin_id={api_id}&product_id={order_id}'.format(
            api_id=KAKAO_PAY_ONE_CLICK_API_ID,
            order_id=order.order_id
        )
    else:
        oneclick_url = 'kakaotalk://bizplugin?plugin_id={api_id}&oneclick_id={order_id}'.format(
            api_id=KAKAO_PAY_ONE_CLICK_API_ID,
            order_id=order.order_id
        )

    buttons = [
        {
            'action': 'osLink',
            'label': '카카오페이 결제',
            'messageText': KAKAO_EMOJI_LOADING,
            'osLink': {
                'android': oneclick_url,
                'ios': oneclick_url,
            },
        },
        {
            'action': 'webLink',
            'label': '신용카드 결제',
            'messageText': KAKAO_EMOJI_LOADING,
            'extra': dataActionExtra,
            'webLinkUrl': '{host_url}/payment?merchant_uid={merchant_uid}'.format(
                host_url=host_url,
                merchant_uid=order.order_id,
            )
        },
    ]

    discount = applyDiscount(user, menu)

    kakaoForm.ComerceCard_Push(
        description,
        order.totalPrice,
        None,
        thumbnails,
        profile,
        buttons
    )

    kakaoForm.ComerceCard_Add()

    buttons = [
        {
            'action': 'block',
            'label': '주문 확인하기',
            'messageText': KAKAO_EMOJI_LOADING,
            'blockId': KAKAO_BLOCK_USER_SET_ORDER_SHEET,
            'extra': dataActionExtra,
        },
    ]

    KakaoInstantForm().Message(
        '\'결제 완료\' 후 주문을 확인해주세요.',
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
        return errorView('잘못된 블럭 경로', '정상적이지 않은 경로거나, 오류가 발생했습니다.\n다시 주문해주세요.')

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

    '''
    if (orderRecordSheet.timeoutValidation()):
        orderRecordSheet.recordUpdate(user, order, ORDER_RECORD_TIMEOUT)
        return kakaoView_TimeOut(KAKAO_BLOCK_USER_SET_ORDER_SHEET)
        else:
    '''
    orderRecordSheet.recordUpdate(user, order, ORDER_RECORD_PAYMENT_CONFIRM)

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
        isPickupZone = menu.tag.filter(name='픽업존').exists()

        KakaoInstantForm().Message(
            '🛑  아직 결제가 완료되지 않았어요.',
            '결제 금액을 확인하시고 결제해주세요.',
            kakaoForm=kakaoForm
        )

        # Menu Carousel Card Add
        thumbnails = [
            {
                'imageUrl': None,
                'fixedRatio': 'true',
                'width': 800,
                'height': 800,
            }
        ]

        if(isPickupZone):
            description = '주문금액 {amount}원 + 이용료 {delivery_fee}원'.format(
                amount=(order.totalPrice - order.delivery_fee),
                delivery_fee=order.delivery_fee,
            )
        else:
            isCafe = store.category.filter(name='카페').exists()
            if(isCafe):
                description = '픽업 시간 : {pickup_time}'.format(pickup_time=order.pickup_time.strftime(
                    '%-m월 %-d일 오전 11시 30분 ~ 오후 2시'))
            else:
                description = '픽업 시간 : {pickup_time}'.format(pickup_time=order.pickup_time.strftime(
                    '%p %-I시 %-M분').replace('AM', '오전').replace('PM', '오후'))

        profile = {
            'nickname': '{} - {}'.format(menu.store.name, menu.name),
            'imageUrl': '{}{}'.format(HOST_URL, store.logoImgURL()),
        }

        host_url = 'https://www.eatple.com'

        if(False and settings.SETTING_ID == 'DEBUG'):
            oneclick_url = 'kakaotalk://bizplugin?plugin_id={api_id}&product_id={order_id}'.format(
                api_id=KAKAO_PAY_ONE_CLICK_API_ID,
                order_id=order.order_id
            )
        else:
            oneclick_url = 'kakaotalk://bizplugin?plugin_id={api_id}&oneclick_id={order_id}'.format(
                api_id=KAKAO_PAY_ONE_CLICK_API_ID,
                order_id=order.order_id
            )

        buttons = [
            {
                'action': 'osLink',
                'label': '카카오페이 결제',
                'messageText': KAKAO_EMOJI_LOADING,
                'osLink': {
                    'android': oneclick_url,
                    'ios': oneclick_url,
                },
            },
            {
                'action': 'webLink',
                'label': '신용카드 결제',
                'messageText': KAKAO_EMOJI_LOADING,
                'extra': dataActionExtra,
                'webLinkUrl': '{host_url}/payment?merchant_uid={merchant_uid}'.format(
                    host_url=host_url,
                    merchant_uid=order.order_id,
                )
            },
        ]

        discount = applyDiscount(user, menu)

        kakaoForm.ComerceCard_Push(
            description,
            order.totalPrice,
            None,
            thumbnails,
            profile,
            buttons
        )

        kakaoForm.ComerceCard_Add()
        buttons = {
            'action': 'block',
            'label': '주문 확인하기',
            'messageText': KAKAO_EMOJI_LOADING,
            'blockId': KAKAO_BLOCK_USER_SET_ORDER_SHEET,
            'extra': dataActionExtra,
        },

        KakaoInstantForm().Message(
            '\'결제 완료\' 후 주문을 확인해주세요.',
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
            '주문이 정상적으로 확인되었습니다.',
            '아래 잇플패스를 확인해주세요.',
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
def GET_Store(request):
    EatplusSkillLog('GET_Store')

    kakaoPayload = KakaoPayLoad(request)

    # User Validation
    user = userValidation(kakaoPayload)
    if (user == None):
        return GET_UserHome(request)

    Pixel_viewStore(user)

    # User Case
    if(isB2BUser(user)):
        return GET_B2B_Store(request)
    else:
        if(isServiceArea(user)):
            return kakaoView_StoreListup(kakaoPayload)
        else:
            return kakaoView_MenuListupWithAreaOut(kakaoPayload)


@csrf_exempt
def GET_Menu(request):
    EatplusSkillLog('GET_Menu')

    kakaoPayload = KakaoPayLoad(request)

    # User Validation
    user = userValidation(kakaoPayload)
    if (user == None):
        return GET_UserHome(request)

    Pixel_viewMenu(user)

    # User Case
    if(isB2BUser(user)):
        return GET_B2B_Menu(request)
    else:
        if(isServiceArea(user)):
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

        Pixel_setPickupTime(user)

        if(isB2BUser(user)):
            return SET_B2B_PickupTime(request)
        else:
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

        Pixel_orderSheet(user)

        if(isB2BUser(user)):
            return SET_B2B_OrderSheet(request)
        else:
            # Block Validation
            prev_block_id = prevBlockValidation(kakaoPayload)
            if(prev_block_id != KAKAO_BLOCK_USER_SET_PICKUP_TIME and prev_block_id != KAKAO_BLOCK_USER_SET_ORDER_SHEET):
                return errorView('잘못된 블럭 경로', '정상적이지 않은 경로거나, 오류가 발생했습니다.\n다시 주문해주세요.')

            if(prev_block_id == KAKAO_BLOCK_USER_SET_PICKUP_TIME):
                return kakaoView_OrderPayment(kakaoPayload)
            elif(prev_block_id == KAKAO_BLOCK_USER_SET_ORDER_SHEET):
                return kakaoView_OrderPaymentCheck(kakaoPayload)

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView('{}'.format(ex))
