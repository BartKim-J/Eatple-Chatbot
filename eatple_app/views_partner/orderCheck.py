# View-System
from eatple_app.views_system.include import *
from eatple_app.views_system.debugger import *

# # # # # # # # # # # # # # # # # # # # # # # # #
#
# Static View
#
# # # # # # # # # # # # # # # # # # # # # # # # #


def orderCheckTimeValidation():
    orderTimeSheet = OrderTimeSheet()
    currentDate = orderTimeSheet.GetCurrentDate()
    currentDateWithoutTime = orderTimeSheet.GetCurrentDateWithoutTime()

    # DEBUG
    if(VALIDATION_DEBUG_MODE):
        return True

    # Prev Lunch Order Time
    lunchCheckTimeStart = orderTimeSheet.GetPrevLunchOrderTimeEnd()

    lunchCheckTimeStart = lunchCheckTimeStart

    lunchCheckTimeEnd = orderTimeSheet.GetLunchOrderPickupTimeEnd()

    if(lunchCheckTimeStart < currentDate) and (currentDate < lunchCheckTimeEnd):
        return True

    return False


def kakaoView_OrderDetails(kakaoPayload):
    kakaoForm = KakaoForm()

    # Partner Validation
    partner = partnerValidation(kakaoPayload)
    if (partner == None):
        return errorView('잘못된 사용자 계정', '찾을 수 없는 사용자 계정 아이디입니다.')

    ORDER_LIST_QUICKREPLIES_MAP = [
        {
            'action': 'block',
            'label': '🏠  홈',
            'messageText': '🏠  홈',
            'blockId': KAKAO_BLOCK_PARTNER_HOME,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_PARTNER_GET_ORDER_DETAILS
            }
        },
    ]

    if(orderCheckTimeValidation()):
        orderManager = PartnerOrderManager(partner)
        orderManager.orderPaidCheck()
        orderManager.orderPenddingCleanUp()

        availableOrders = orderManager.getAvailableOrders()

        currentTime = dateNowByTimeZone()

        if(availableOrders.exists() == True):
            isCafe = partner.store.category.filter(name="카페").exists()
            isPickupZone = Menu.objects.filter(
                store=partner.store).filter(tag__name="픽업존").exists()
            isNormalMenu = Menu.objects.filter(
                store=partner.store).filter(
                    ~Q(tag__name="픽업존") and
                    ~Q(tag__name="카페")
            ).exists()

            pickupZoneMenu = Menu.objects.filter(
                store=partner.store).filter(tag__name="픽업존")
            pickupTimes = PickupTime.objects.all()

            if(isCafe or isPickupZone):
                orderTimeSheet = OrderTimeSheet()

                menuList = Menu.objects.filter(
                    store=partner.store, status=OC_OPEN).filter(
                        Q(tag__name="픽업존") |
                        Q(tag__name="카페")
                )

                if(isPickupZone):
                    time = '오전 11시 30분'

                    # @Temporary Code
                    if(partner.store.name == '봉된장'):
                        time = '오전 11시 50분'
                    else:
                        if(partner.store.area == STORE_AREA_C_1 or
                           partner.store.area == STORE_AREA_C_2 or
                           partner.store.area == STORE_AREA_C_3):
                            time = '오전 11시 30분'
                        elif(partner.store.area == STORE_AREA_C_5):
                            time = '오전 11시 50분'

                    title = '{} {}'.format(
                        datetime.datetime.now().strftime("%-m월 %-d일"),
                        time
                    )

                else:
                    title = '상시 픽업'

                header = {
                    'title': title,
                    'imageUrl': '{}{}'.format(HOST_URL, PARTNER_ORDER_SHEET_IMG),
                }

                if(menuList):
                    totalCount = 0

                    for menu in menuList:
                        orderByMenu = Order.objects.filter(menu=menu).filter(
                            (
                                Q(status=ORDER_STATUS_PICKUP_COMPLETED) |
                                Q(status=ORDER_STATUS_PICKUP_WAIT) |
                                Q(status=ORDER_STATUS_PICKUP_PREPARE) |
                                Q(status=ORDER_STATUS_ORDER_CONFIRM_WAIT) |
                                Q(status=ORDER_STATUS_ORDER_CONFIRMED)
                            ) &
                            Q(menu=menu) &
                            Q(pickup_time__gte=orderTimeSheet.GetLunchOrderPickupTimeStart())
                        )

                        totalCount += orderByMenu.count()

                        if(orderByMenu.count() > 0):
                            imageUrl = '{}{}'.format(HOST_URL, menu.imgURL())
                            if(partner.store.name == '마치래빗샐러드'):
                                kakaoForm.ListCard_Push(
                                    '{}'.format(menu.name),
                                    '들어온 주문 : {}개 / {}원'.format(
                                        orderByMenu.count(), format(orderByMenu.first().totalPrice * orderByMenu.count(), ',')),
                                    imageUrl,
                                    None
                                )
                            else:
                                kakaoForm.ListCard_Push(
                                    '{}'.format(menu.name),
                                    '들어온 주문 : {}개'.format(orderByMenu.count()),
                                    imageUrl,
                                    None
                                )
                        else:
                            pass

                    if(totalCount > 0):
                        kakaoForm.ListCard_Add(header)
                    else:
                        pass
                else:
                    pass

            if(isNormalMenu):
                for pickupTime in pickupTimes:
                    menuList = Menu.objects.filter(
                        store=partner.store, pickup_time=pickupTime, status=OC_OPEN).filter(
                            ~Q(tag__name="픽업존") &
                            ~Q(tag__name="카페")
                    )

                    if(menuList.exists() == False):
                        continue

                    refPickupTime = [x.strip()
                                     for x in str(pickupTime.time).split(':')]
                    datetime_pickup_time = currentTime.replace(
                        hour=int(refPickupTime[0]),
                        minute=int(refPickupTime[1]),
                        second=0,
                        microsecond=0
                    )

                    header = {
                        'title': '{pickupTime}'.format(
                            pickupTime=datetime_pickup_time.strftime(
                                '%-m월 %-d일 %p %-I시 %-M분').replace('AM', '오전').replace('PM', '오후'),
                        ),
                        'imageUrl': '{}{}'.format(HOST_URL, PARTNER_ORDER_SHEET_IMG),
                    }

                    if(menuList):
                        totalCount = 0
                        for menu in menuList:
                            orderByPickupTime = Order.objects.filter(menu=menu).filter(
                                (
                                    Q(status=ORDER_STATUS_PICKUP_COMPLETED) |
                                    Q(status=ORDER_STATUS_PICKUP_WAIT) |
                                    Q(status=ORDER_STATUS_PICKUP_PREPARE) |
                                    Q(status=ORDER_STATUS_ORDER_CONFIRM_WAIT) |
                                    Q(status=ORDER_STATUS_ORDER_CONFIRMED)
                                ) &
                                Q(pickup_time=datetime_pickup_time)
                            )
                            orderCount = orderByPickupTime.count()

                            totalCount += orderCount

                            if(orderCount > 0):
                                imageUrl = '{}{}'.format(
                                    HOST_URL, menu.imgURL())

                                if(partner.store.name == '마치래빗샐러드'):
                                    kakaoForm.ListCard_Push(
                                        '{}'.format(menu.name),
                                        '들어온 주문 : {}개 / {}원'.format(
                                            orderCount, format(orderByPickupTime.first().totalPrice * orderCount, ',')),
                                        imageUrl,
                                        None
                                    )
                                else:
                                    kakaoForm.ListCard_Push(
                                        '{}'.format(menu.name),
                                        '들어온 주문 : {}개'.format(orderCount),
                                        imageUrl,
                                        None
                                    )
                            else:
                                pass

                        if(totalCount > 0):
                            kakaoForm.ListCard_Add(header)
        else:
            kakaoForm.BasicCard_Push(
                '오늘은 들어온 주문이 없어요.',
                '',
                {},
                []
            )
            kakaoForm.BasicCard_Add()
    else:
        kakaoForm.BasicCard_Push(
            '아직 주문조회 가능시간이 아닙니다.',
            ' 점심 주문조회 가능시간\n - 오전 11시 ~ 오후 2시',
            {},
            []
        )

        kakaoForm.BasicCard_Add()

    kakaoForm.QuickReplies_AddWithMap(ORDER_LIST_QUICKREPLIES_MAP)

    return JsonResponse(kakaoForm.GetForm())

# @TODO


def kakaoView_CalculateDetails(kakaoPaylaod):
    # Partner Validation
    partner = partnerValidation(kakaoPayload)
    if (partner == None):
        return errorView('잘못된 사용자 계정', '찾을 수 없는 사용자 계정 아이디입니다.')

    return errorView('{}'.format(ex))


# # # # # # # # # # # # # # # # # # # # # # # # #
#
# External View
#
# # # # # # # # # # # # # # # # # # # # # # # # #

@csrf_exempt
def GET_ParnterOrderDetails(request):
    EatplusSkillLog('GET_ParnterOrderDetails')
    try:
        kakaoPayload = KakaoPayLoad(request)

        # User Validation
        partner = partnerValidation(kakaoPayload)
        if (partner == None):
            return GET_PartnerHome(request)

        return kakaoView_OrderDetails(kakaoPayload)

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView('{} '.format(ex))


@csrf_exempt
def GET_CalculateDetails(request):
    EatplusSkillLog('GET_CalculateDetails')
    try:
        kakaoPayload = KakaoPayLoad(request)

        # User Validation
        partner = partnerValidation(kakaoPayload)
        if (partner == None):
            return GET_PartnerHome(request)

        return kakaoView_CalculateDetails(kakaoPayload)

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView('{} '.format(ex))
