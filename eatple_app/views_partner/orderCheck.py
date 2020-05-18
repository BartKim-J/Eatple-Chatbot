# View-System
from eatple_app.views_system.include import *
from eatple_app.views_system.debugger import *

# # # # # # # # # # # # # # # # # # # # # # # # #
#
# Static View
#
# # # # # # # # # # # # # # # # # # # # # # # # #

CONTEXT_LINE = '―――――――――――――\n'


def orderCheckTimeValidation():
    orderTimeSheet = OrderTimeSheet()
    currentDate = orderTimeSheet.GetCurrentDate()
    currentDateWithoutTime = orderTimeSheet.GetCurrentDateWithoutTime()

    # DEBUG
    if(VALIDATION_DEBUG_MODE):
        return True

    lunchCheckTimeStart = orderTimeSheet.GetPrevLunchOrderTimeEnd()
    lunchCheckTimeEnd = orderTimeSheet.GetLunchOrderPickupTimeEnd()

    dinnerCheckTimeStart = orderTimeSheet.GetDinnerOrderTimeEnd()
    dinnerCheckTimeEnd = orderTimeSheet.GetNextLunchOrderEditTimeStart()

    if(lunchCheckTimeStart < currentDate) and (currentDate < lunchCheckTimeEnd):
        return SELLING_TIME_LUNCH

    if(dinnerCheckTimeStart < currentDate) and (currentDate < dinnerCheckTimeEnd):
        return SELLING_TIME_DINNER

    return None


def kakaoView_OrderDetails(kakaoPayload):
    kakaoForm = KakaoForm()

    # Partner Validation
    partner = partnerValidation(kakaoPayload)
    if (partner == None):
        return errorView('잘못된 사용자 계정', '찾을 수 없는 사용자 계정 아이디입니다.')

    store = storeValidation(kakaoPayload)
    if (store == None):
        return errorView('잘못된 주문 경로', '처음부터 다시 주문해주세요.')

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

    buttons = [
    ]

    if(orderCheckTimeValidation() != None):
        if(partner.is_staff == False):
            store.orderChecked()

        orderManager = PartnerOrderManager(partner)
        orderManager.orderPaidCheck()
        orderManager.orderPenddingCleanUp()

        availableOrders = orderManager.getAvailableOrders()

        currentTime = dateNowByTimeZone()

        if(availableOrders.exists() == True):
            isCafe = store.category.filter(name="카페").exists()
            isPickupZone = Menu.objects.filter(
                store=store).filter(tag__name="픽업존").exists()
            isNormalMenu = Menu.objects.filter(
                store=store).filter(
                    ~Q(tag__name="픽업존") and
                    ~Q(tag__name="카페")
            ).exists()

            pickupZoneMenu = Menu.objects.filter(
                store=store).filter(tag__name="픽업존")
            pickupTimes = PickupTime.objects.all()

            if(isPickupZone):
                orderTimeSheet = OrderTimeSheet()

                for pickupTime in pickupTimes:
                    menuList = Menu.objects.filter(
                        tag__name="픽업존",
                        store=store,
                        pickup_time=pickupTime,
                        status=OC_OPEN
                    )

                    refPickupTime = [x.strip()
                                     for x in str(pickupTime.time).split(':')]
                    datetime_pickup_time = currentTime.replace(
                        hour=int(refPickupTime[0]),
                        minute=int(refPickupTime[1]),
                        second=0,
                        microsecond=0
                    )

                    if(store.name == '봉된장'):
                        time = datetime.timedelta(minutes=30)
                    else:
                        if(store.area == STORE_AREA_C_1 or
                                store.area == STORE_AREA_C_2 or
                                store.area == STORE_AREA_C_3):
                            time = datetime.timedelta(minutes=40)
                        elif(store.area == STORE_AREA_C_5):
                            time = datetime.timedelta(minutes=20)
                        else:
                            time = datetime.timedelta(minutes=0)

                    delivery_pickup_time = datetime_pickup_time - time
                    title = '{pickupTime}'.format(
                        pickupTime=delivery_pickup_time.strftime(
                            '%-m월 %-d일 %p %-I시 %-M분').replace('AM', '오전').replace('PM', '오후')
                    )

                    context = CONTEXT_LINE

                    if(menuList):
                        totalCount = 0
                        totalAmount = 0

                        for menu in menuList:
                            orderByMenu = Order.objects.filter(menu=menu).filter(
                                (
                                    Q(status=ORDER_STATUS_PICKUP_COMPLETED) |
                                    Q(status=ORDER_STATUS_PICKUP_WAIT) |
                                    Q(status=ORDER_STATUS_PICKUP_PREPARE) |
                                    Q(status=ORDER_STATUS_ORDER_CONFIRM_WAIT) |
                                    Q(status=ORDER_STATUS_ORDER_CONFIRMED)
                                ) &
                                Q(pickup_time=datetime_pickup_time)
                            )

                            if(orderByMenu.count() > 0):
                                amount = (orderByMenu.first(
                                ).totalPrice - orderByMenu.first().delivery_fee) * orderByMenu.count()

                                totalCount += orderByMenu.count()
                                totalAmount += amount

                                context += '{menu} - {count}개 / {amount}원\n'.format(
                                    menu=menu.name,
                                    count=orderByMenu.count(),
                                    amount=format(amount, ',')
                                )
                            else:
                                pass

                        if(totalCount > 0):
                            total_context = '총 {totalCount}개 - {totalAmount}원\n'.format(
                                totalCount=totalCount,
                                totalAmount=format(totalAmount, ','),
                            )

                            total_context += context

                            kakaoForm.BasicCard_Push(
                                title,
                                total_context,
                                {},
                                [],
                            )
                            kakaoForm.BasicCard_Add()
                        else:
                            pass
                else:
                    pass

            elif(isCafe):
                pass

            if(isNormalMenu):
                for pickupTime in pickupTimes:
                    menuList = Menu.objects.filter(
                        store=store, pickup_time=pickupTime, status=OC_OPEN).filter(
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

                    title = '{pickupTime}'.format(
                        pickupTime=datetime_pickup_time.strftime(
                            '%-m월 %-d일 %p %-I시 %-M분').replace('AM', '오전').replace('PM', '오후')
                    )

                    context = CONTEXT_LINE

                    if(menuList):
                        totalCount = 0
                        totalAmount = 0

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

                            if(orderByPickupTime.count() > 0):
                                amount = (orderByPickupTime.first(
                                ).totalPrice - orderByPickupTime.first().delivery_fee) * orderByPickupTime.count()

                                totalCount += orderByPickupTime.count()
                                totalAmount += amount

                                context += '{menu} - {count}개 / {amount}원\n'.format(
                                    menu=menu.name,
                                    count=orderByPickupTime.count(),
                                    amount=format(amount, ',')
                                )
                            else:
                                pass

                        if(totalCount > 0):
                            total_context = '총 {totalCount}개 - {totalAmount}원\n'.format(
                                totalCount=totalCount,
                                totalAmount=format(totalAmount, ','),
                            )

                            total_context += context

                            kakaoForm.BasicCard_Push(
                                title,
                                total_context,
                                {},
                                [],
                            )
                            kakaoForm.BasicCard_Add()
                        else:
                            pass
        else:
            kakaoForm.BasicCard_Push(
                '오늘은 들어온 주문이 없어요.',
                '',
                {},
                []
            )
            kakaoForm.BasicCard_Add()
    else:
        if(dateNowByTimeZone() <= dateNowByTimeZone().replace(hour=12)):
            subtext = ' 점심 주문조회 가능시간\n - 오전 11시 ~ 오후 2시'
        else:
            subtext = ' 저녁 주문조회 가능시간\n - 오후 6시 ~ 오후 9시'

        kakaoForm.BasicCard_Push(
            '아직 주문조회 가능시간이 아닙니다.',
            subtext,
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
