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

    lunchCheckTimeStart = orderTimeSheet.GetPrevLunchOrderTimeEnd()
    lunchCheckTimeEnd = orderTimeSheet.GetLunchOrderPickupTimeEnd()

    dinnerCheckTimeStart = orderTimeSheet.GetDinnerOrderTimeEnd()
    dinnerCheckTimeEnd = orderTimeSheet.GetNextLunchOrderEditTimeStart()

    if(lunchCheckTimeStart < currentDate) and (currentDate < lunchCheckTimeEnd):
        return SELLING_TIME_LUNCH

    if(dinnerCheckTimeStart < currentDate) and (currentDate < dinnerCheckTimeEnd):
        return SELLING_TIME_DINNER

    return None


def pickupZone_component(partner, store, kakaoForm):
    currentTime = dateNowByTimeZone()

    pickupTimes = PickupTime.objects.all()

    for pickupTime in pickupTimes:
        if(store != None):
            menuList = Menu.objects.filter(
                tag__name="픽업존",
                store=store,
                pickup_time=pickupTime,
                status=OC_OPEN
            )
        else:
            storeList = Store.objects.filter(
                crn__CRN_id=partner.store.crn.CRN_id)
            menuList = Menu.objects.none()
            for storeEntry in storeList:
                menuList |= Menu.objects.filter(
                    tag__name="픽업존",
                    store=storeEntry,
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

        if(partner.store.name == '봉된장'):
            time = datetime.timedelta(minutes=30)
        else:
            if(partner.store.area == STORE_AREA_C_1 or
                    partner.store.area == STORE_AREA_C_2 or
                    partner.store.area == STORE_AREA_C_3):
                time = datetime.timedelta(minutes=40)
            elif(partner.store.area == STORE_AREA_C_5):
                time = datetime.timedelta(minutes=20)
            else:
                time = datetime.timedelta(minutes=0)

        if(store != None):
            storeName = ' - {}'.format(store.name)
        else:
            storeName = ''

        delivery_pickup_time = datetime_pickup_time - time
        title = '{pickupTime}{store}'.format(
            store=storeName,
            pickupTime=delivery_pickup_time.strftime(
                '%-m/%-d %p %-I시 %-M분').replace('AM', '오전').replace('PM', '오후')
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
                    amount = orderByMenu.first().menu.price * \
                        orderByMenu.count()

                    totalCount += orderByMenu.count()
                    totalAmount += amount

                    if(menu.name_partner != None):
                        menuName = menu.name_partner
                    else:
                        menuName = menu.name

                    if(menu.store.name == '마치래빗샐러드'):
                        context += '{menu} {count}개 / {amount}원\n'.format(
                            store=menu.store.name,
                            menu=menuName,
                            count=orderByMenu.count(),
                            amount=format(amount, ',')
                        )
                    else:
                        if(store != None):
                            storeName = ''
                        else:
                            storeName = '{} / '.format(menu.store.name)

                        context += '{store}{menu} {count}개\n'.format(
                            store=storeName,
                            menu=menuName,
                            count=orderByMenu.count(),
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


def normal_component(partner, store, kakaoForm):
    currentTime = dateNowByTimeZone()

    pickupTimes = PickupTime.objects.all()

    for pickupTime in pickupTimes:
        if(store != None):
            menuList = Menu.objects.filter(
                store=store, pickup_time=pickupTime, status=OC_OPEN).filter(
                    ~Q(tag__name="픽업존") &
                    ~Q(tag__name="카페")
            )
        else:
            storeList = Store.objects.filter(
                crn__CRN_id=partner.store.crn.CRN_id)
            menuList = Menu.objects.none()
            for storeEntry in storeList:
                menuList |= Menu.objects.filter(
                    store=storeEntry, pickup_time=pickupTime, status=OC_OPEN).filter(
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

        if(store != None):
            storeName = ' - {}'.format(store.name)
        else:
            storeName = ''

        title = '{pickupTime}{store}'.format(
            store=storeName,
            pickupTime=datetime_pickup_time.strftime(
                '%-m/%-d %p %-I시 %-M분').replace('AM', '오전').replace('PM', '오후')
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
                    amount = orderByMenu.first().menu.price * orderByPickupTime.count()

                    totalCount += orderByPickupTime.count()
                    totalAmount += amount

                    if(menu.name_partner != None):
                        menuName = menu.name_partner
                    else:
                        menuName = menu.name

                    if(menu.store.name == '마치래빗샐러드'):
                        context += '{menu} {count}개 / {amount}원\n'.format(
                            store=menu.store.name,
                            menu=menuName,
                            count=orderByPickupTime.count(),
                            amount=format(amount, ',')
                        )
                    else:
                        if(store != None):
                            storeName = ''
                        else:
                            storeName = '{} / '.format(menu.store.name)

                        context += '{store}{menu} {count}개\n'.format(
                            store=storeName,
                            menu=menuName,
                            count=orderByPickupTime.count(),
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


def kakaoView_OrderDetails(kakaoPayload):
    kakaoForm = KakaoForm()

    # Partner Validation
    partner = partnerValidation(kakaoPayload)
    if (partner == None):
        return errorView('잘못된 사용자 계정', '찾을 수 없는 사용자 계정 아이디입니다.')

    storeList = Store.objects.filter(
        Q(crn__CRN_id=partner.store.crn.CRN_id)
    )

    store = storeValidation(kakaoPayload)

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

    if(orderCheckTimeValidation() != None):
        if(partner.is_staff == False):
            if(store != None):
                store.orderChecked()
            else:
                for storeEntry in storeList:
                    storeEntry.orderChecked()

        storeList = Store.objects.filter(
            Q(crn__CRN_id=partner.store.crn.CRN_id)
        )
        availableOrders = 0

        if(store == None):
            for storeEntry in storeList:
                orderManager = PartnerOrderManager(partner, store=storeEntry)
                orderManager.orderPaidCheck()
                orderManager.orderPenddingCleanUp()

                availableOrders += orderManager.getAvailableOrders().count()
        else:
            orderManager = PartnerOrderManager(partner, store=store)
            orderManager.orderPaidCheck()
            orderManager.orderPenddingCleanUp()

            availableOrders += orderManager.getAvailableOrders().count()

        if(availableOrders > 0):
            if (store == None):
                isCafe = False
                isPickupZone = False
                isNormalMenu = False

                for storeEntry in storeList:
                    isCafe |= storeEntry.category.filter(name="카페").exists()
                    isPickupZone |= Menu.objects.filter(
                        store=storeEntry).filter(tag__name="픽업존").exists()
                    isNormalMenu |= Menu.objects.filter(
                        store=storeEntry).filter(
                            ~Q(tag__name="픽업존") and
                            ~Q(tag__name="카페")
                    ).exists()
            else:
                isCafe = store.category.filter(name="카페").exists()
                isPickupZone = Menu.objects.filter(
                    store=store).filter(tag__name="픽업존").exists()
                isNormalMenu = Menu.objects.filter(
                    store=store).filter(
                        ~Q(tag__name="픽업존") and
                        ~Q(tag__name="카페")
                ).exists()

            if(isPickupZone):
                pickupZone_component(partner, store, kakaoForm)
            elif(isCafe):
                pass

            if(isNormalMenu):
                normal_component(partner, store, kakaoForm)
        else:
            if(store != None and storeList.count() > 1):
                storeName = '매장 : {}'.format(store.name)
            else:
                storeName = ''

            kakaoForm.BasicCard_Push(
                '오늘은 들어온 주문이 없어요.',
                storeName,
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

    if(store != None):
        storeList = Store.objects.filter(
            Q(crn__CRN_id=partner.store.crn.CRN_id) &
            ~Q(name=store.name)
        )
    else:
        if(storeList.count() > 1):
            storeList = Store.objects.filter(
                Q(crn__CRN_id=partner.store.crn.CRN_id)
            )
        else:
            pass
    for storeEntry in storeList:
        ORDER_LIST_QUICKREPLIES_MAP.insert(0,
                                           {
                                               'action': 'block',
                                               'label': storeEntry.name,
                                               'messageText': KAKAO_EMOJI_LOADING,
                                               'blockId': KAKAO_BLOCK_PARTNER_GET_ORDER_DETAILS,
                                               'extra': {
                                                   KAKAO_PARAM_STORE_ID: storeEntry.store_id,
                                                   KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_PARTNER_GET_ORDER_DETAILS
                                               }
                                           },
                                           )

    kakaoForm.QuickReplies_AddWithMap(ORDER_LIST_QUICKREPLIES_MAP)

    return JsonResponse(kakaoForm.GetForm())


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
