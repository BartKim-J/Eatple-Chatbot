from django.contrib.admin.models import LogEntry

from django.shortcuts import render

# Models
from eatple_app.models import *

# Define
from eatple_app.define import *

########################################################################
# METHOD

WEEKDAY = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']


def getOrderChart(orderTimeSheet, isStaff=False):
    currentDate = orderTimeSheet.GetCurrentDate()
    currentDateWithoutTime = orderTimeSheet.GetCurrentDateWithoutTime()

    deadline = orderTimeSheet.GetInitialCountTime()

    if(currentDate < deadline):
        currentDateWithoutTime = currentDateWithoutTime
    else:
        currentDateWithoutTime = currentDateWithoutTime + \
            datetime.timedelta(days=1)

    label = ''
    data = ''

    checkDate = currentDateWithoutTime - datetime.timedelta(days=34)

    checkDate = checkDate + \
        datetime.timedelta(days=(0 - checkDate.weekday()))

    while(not ((checkDate >= currentDateWithoutTime) and (checkDate.weekday() == 5))):
        prevLunchOrderEditTimeStart = checkDate + \
            datetime.timedelta(hours=21, minutes=0, days=-1)
        nextLunchOrderEditTimeStart = checkDate + \
            datetime.timedelta(hours=21, minutes=0)

        if(prevLunchOrderEditTimeStart.strftime('%A') == 'Friday' and
           nextLunchOrderEditTimeStart.strftime('%A') == 'Saturday'):
            pass
        elif(prevLunchOrderEditTimeStart.strftime('%A') == 'Saturday' and
             nextLunchOrderEditTimeStart.strftime('%A') == 'Sunday'):
            pass
        else:
            label += '{} {},'.format(checkDate.strftime(
                '%-m월 %-d일').replace('AM', '오전').replace('PM', '오후'),
                WEEKDAY[checkDate.weekday()])

            staffFilter = Q()
            if(isStaff):
                staffFilter.add(
                    Q(ordersheet__user__is_staff=False), staffFilter.AND)

            data += '{},'.format((
                Order.objects.filter(
                    Q(payment_date__gte=prevLunchOrderEditTimeStart) &
                    Q(payment_date__lt=nextLunchOrderEditTimeStart) &
                    Q(payment_status=EATPLE_ORDER_STATUS_PAID) &
                    staffFilter
                ).count())
            )

        checkDate = checkDate + datetime.timedelta(days=1)

    label = replaceRight(label, ',', '', 1)
    data = replaceRight(data, ',', '', 1)

    return {
        'label': label,
        'data': data
    }


def getPickupTimeChart(orderTimeSheet):
    currentDate = orderTimeSheet.GetCurrentDate()
    currentDateWithoutTime = orderTimeSheet.GetCurrentDateWithoutTime()

    deadline = orderTimeSheet.GetInitialCountTime()

    if(currentDate < deadline):
        currentDateWithoutTime = currentDateWithoutTime
    else:
        currentDateWithoutTime = currentDateWithoutTime + \
            datetime.timedelta(days=1)

    label = ''
    data = ''

    checkHours = 5
    minuteInterval = 5

    for i in range(int(60/minuteInterval) * checkHours):
        checkData = currentDateWithoutTime + \
            datetime.timedelta(
                days=0, hours=11, minutes=30 + (minuteInterval * i))

        startTime = checkData
        endTime = checkData + datetime.timedelta(minutes=minuteInterval)

        if(startTime >= currentDate):
            label += '픽업시간이 아님,'
        else:
            label += '{} ~ {},'.format(startTime.strftime(
                '%p %-I시 %-M분').replace('AM', '오전').replace('PM', '오후'),
                endTime.strftime(
                '%p %-I시 %-M분').replace('AM', '오전').replace('PM', '오후')
            )

        data += '{},'.format((
            Order.objects.filter(
                Q(pickup_complete_date__gte=startTime) &
                Q(pickup_complete_date__lt=endTime) &
                Q(payment_status=EATPLE_ORDER_STATUS_PAID) &
                Q(status=ORDER_STATUS_PICKUP_COMPLETED)
            ).count())
        )

    label = replaceRight(label, ',', '', 1)
    data = replaceRight(data, ',', '', 1)

    return {
        'label': label,
        'data': data
    }


def getDailyOrderChart(orderTimeSheet, isStaff=False):
    currentDate = orderTimeSheet.GetCurrentDate()
    currentDateWithoutTime = orderTimeSheet.GetCurrentDateWithoutTime()

    deadline = orderTimeSheet.GetInitialCountTime()

    if(currentDate < deadline):
        startTime = orderTimeSheet.GetPrevLunchOrderEditTimeStart()
    else:
        startTime = orderTimeSheet.GetNextLunchOrderEditTimeStart()

    label = ''
    data = ''

    for i in range(24):
        checkStartTime = startTime + datetime.timedelta(hours=i)
        cehckEndTime = startTime + datetime.timedelta(hours=i+1)

        label += '{},'.format(checkStartTime.strftime(
            '%-m월 %-d일 %p %-I시 %-M분 ~').replace('AM', '오전').replace('PM', '오후'))

        staffFilter = Q()
        if(isStaff):
            staffFilter.add(
                Q(ordersheet__user__is_staff=False), staffFilter.AND)

        data += '{},'.format((
            Order.objects.filter(
                Q(payment_date__gte=checkStartTime) &
                Q(payment_date__lt=cehckEndTime) &
                Q(payment_status=EATPLE_ORDER_STATUS_PAID) &
                staffFilter
            ).count())
        )

    label = replaceRight(label, ',', '', 1)
    data = replaceRight(data, ',', '', 1)

    return {
        'label': label,
        'data': data
    }


def getMenuStockChart(menuList):
    label = ''
    data = ''

    menuList = menuList.filter(Q(current_stock__gte=1) & Q(
        status=OC_OPEN) & Q(store__status=OC_OPEN))

    for menu in menuList:
        data += '{},'.format(menu.current_stock)
        label += '{},'.format(menu.name)

    data = replaceRight(data, ',', '', 1)
    label = replaceRight(label, ',', '', 1)

    return {
        'data': data,
        'label': label,
    }


def getDAU(orderTimeSheet):
    currentDate = orderTimeSheet.GetCurrentDate() + datetime.timedelta(days=-1)
    currentDateWithoutTime = orderTimeSheet.GetCurrentDateWithoutTime()

    DAUStartDate = currentDateWithoutTime + datetime.timedelta(days=-1)
    DAUEndDate = currentDateWithoutTime

    DAU = Order.objects.filter(
        Q(payment_date__gte=DAUStartDate) &
        Q(payment_date__lt=DAUEndDate) &
        (
            Q(payment_status=EATPLE_ORDER_STATUS_PAID) |
            Q(payment_status=EATPLE_ORDER_STATUS_CANCELLED) |
            Q(payment_status=EATPLE_ORDER_STATUS_FAILED) |
            Q(payment_status=EATPLE_ORDER_STATUS_NOT_PUSHED) |
            Q(payment_status=EATPLE_ORDER_STATUS_READY)
        )
    ).values_list('ordersheet__user__app_user_id')

    DAU = list(set(DAU))

    return len(DAU)


def getWAU(orderTimeSheet):
    currentDate = orderTimeSheet.GetCurrentDate() + datetime.timedelta(days=-1)
    currentDateWithoutTime = orderTimeSheet.GetCurrentDateWithoutTime()

    WAUStartDate = currentDateWithoutTime - datetime.timedelta(days=7)
    WAUEndDate = currentDateWithoutTime

    WAU = Order.objects.filter(
        Q(payment_date__gte=WAUStartDate) &
        Q(payment_date__lt=WAUEndDate) &
        (
            Q(payment_status=EATPLE_ORDER_STATUS_PAID) |
            Q(payment_status=EATPLE_ORDER_STATUS_CANCELLED) |
            Q(payment_status=EATPLE_ORDER_STATUS_FAILED) |
            Q(payment_status=EATPLE_ORDER_STATUS_NOT_PUSHED) |
            Q(payment_status=EATPLE_ORDER_STATUS_READY)
        )
    ).values_list('ordersheet__user__app_user_id')

    WAU = list(set(WAU))

    return len(WAU)


def getMAU(orderTimeSheet):
    currentDate = orderTimeSheet.GetCurrentDate() + datetime.timedelta(days=-1)
    currentDateWithoutTime = orderTimeSheet.GetCurrentDateWithoutTime()

    MAUStartDate = currentDateWithoutTime - datetime.timedelta(1*365/12)
    MAUEndDate = currentDateWithoutTime

    MAU = Order.objects.filter(
        Q(payment_date__gte=MAUStartDate) &
        Q(payment_date__lt=MAUEndDate) &
        (
            Q(payment_status=EATPLE_ORDER_STATUS_PAID) |
            Q(payment_status=EATPLE_ORDER_STATUS_CANCELLED) |
            Q(payment_status=EATPLE_ORDER_STATUS_FAILED) |
            Q(payment_status=EATPLE_ORDER_STATUS_NOT_PUSHED) |
            Q(payment_status=EATPLE_ORDER_STATUS_READY)
        )
    ).values_list('ordersheet__user__app_user_id')

    MAU = list(set(MAU))

    return len(MAU)


def getWAS(orderTimeSheet):
    currentDate = orderTimeSheet.GetCurrentDate()
    currentDateWithoutTime = orderTimeSheet.GetCurrentDateWithoutTime()

    WAUStartDate = currentDateWithoutTime + datetime.timedelta(days=-7)
    WAUEndDate = currentDateWithoutTime

    WAS = Order.objects.filter(
        Q(payment_date__gte=WAUStartDate) &
        Q(payment_date__lt=WAUEndDate) &
        (
            Q(payment_status=EATPLE_ORDER_STATUS_PAID) |
            Q(payment_status=EATPLE_ORDER_STATUS_CANCELLED) |
            Q(payment_status=EATPLE_ORDER_STATUS_FAILED) |
            Q(payment_status=EATPLE_ORDER_STATUS_NOT_PUSHED) |
            Q(payment_status=EATPLE_ORDER_STATUS_READY)
        )
    ).values_list('store_id')

    WAS = list(set(WAS))

    return len(WAS)


def showActiveStatus(orderTimeSheet):

    MONTH = 4
    DAY = 14

    # Test
    test_start_date = dateNowByTimeZone().replace(year=2020, month=MONTH, day=DAY,
                                                  hour=0, minute=0, second=0, microsecond=0)
    test_end_date = orderTimeSheet.GetCurrentDate()

    WAU_Condition_Date = dateNowByTimeZone().replace(year=2020, month=MONTH, day=DAY,
                                                     hour=0, minute=0, second=0, microsecond=0)
    MAU_Condition_Date = dateNowByTimeZone().replace(year=2020, month=MONTH, day=DAY,
                                                     hour=0, minute=0, second=0, microsecond=0)

    bestDAU = 0
    bestDAUDate = ''

    bestWAU = 0
    bestWAUDate = ''

    bestMAU = 0
    bestMAUDate = ''

    while(test_start_date <= test_end_date):
        test_timeSheet = OrderTimeSheet(test_start_date)
        DAU = getDAU(test_timeSheet)
        WAU = getWAU(test_timeSheet)
        MAU = getMAU(test_timeSheet)

        print('DAU D -', DAU, test_start_date)
        if(bestDAU < DAU):
            bestDAU = DAU
            bestDAUDate = test_start_date

        # print('WAU D -', WAU, test_start_date)
        if(bestWAU < WAU and test_start_date > WAU_Condition_Date):
            bestWAU = WAU
            bestWAUDate = test_start_date

        # print('MAU D -', MAU, test_start_date)
        if(bestMAU < MAU and test_start_date > MAU_Condition_Date):
            bestMAU = MAU
            bestMAUDate = test_start_date

        test_start_date = test_start_date + datetime.timedelta(days=1)

    print(test_start_date)
    print('DAU', bestDAU, bestDAUDate)
    print('WAU', bestWAU, bestWAUDate)
    print('MAU', bestMAU, bestMAUDate)


def getUserInService():
    distance = 500
    ref_gangnam = Point(y=37.497907, x=127.027635, srid=4326)
    ref_yeoksam = Point(y=37.500787, x=127.036919, srid=4326)
    ref_samsung = Point(y=37.508852, x=127.063145, srid=4326)

    queryset = User.objects.all().annotate(
        distance_gangnam=Distance(
            F('location__point'), ref_gangnam) * 100 * 1000,
        distance_yeoksam=Distance(
            F('location__point'), ref_yeoksam) * 100 * 1000,
        distance_samsung=Distance(
            F('location__point'), ref_samsung) * 100 * 1000,
    ).filter(
        (Q(distance_gangnam__lte=distance) &
         Q(distance_gangnam__gte=0)) |
        Q(distance_yeoksam__lte=distance) |
        Q(distance_samsung__lte=distance)
    )
    return queryset


def getUserActive():
    NotAtive = 0
    InActive = 0
    GetActive = 0
    OnActive = 0

    allActive = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    userList = User.objects.all()

    userListInService = getUserInService()

    for user in userList:
        orderList = Order.objects.filter(
            (
                Q(payment_status=EATPLE_ORDER_STATUS_PAID) |
                Q(payment_status=EATPLE_ORDER_STATUS_CANCELLED)
            )
            &
            Q(ordersheet__user=user)
        )

        count = orderList.count()

        if(count == 0):
            allActive[0] += 1

        if(count >= 1):
            allActive[1] += 1
            InActive += 1
        if(count >= 2):
            allActive[2] += 1
            GetActive += 1
        if(count >= 3):
            allActive[3] += 1
            OnActive += 1
        if(count >= 4):
            allActive[4] += 1
        if(count >= 5):
            allActive[5] += 1
        if(count >= 6):
            allActive[6] += 1
        if(count >= 7):
            allActive[7] += 1
        if(count >= 8):
            allActive[8] += 1
        if(count >= 9):
            allActive[9] += 1

    print(allActive)
    data = {
        'userInService': userListInService.count(),
        'notActive': NotAtive,
        'inActive': InActive,
        'getActive': GetActive,
        'onActive': OnActive,
        'allActive': allActive,
    }

    return data


def getOrderDelegated():
    count = 0

    count = Order.objects.filter(
        Q(payment_status=EATPLE_ORDER_STATUS_PAID) &
        ~Q(delegate=None) &
        ~Q(ordersheet__user__is_staff=True)
    ).count()

    return count


def userPersenalData():
    userList = User.objects.all()
    age = 0
    man = 0
    woman = 0

    for user in userList:
        age += 2020 - int(user.birthyear)
        if(user.gender == 'female'):
            woman += 1

    age = age/userList.count()
    woman = woman/userList.count() * 100
    man = 100 - woman

    print('평균나이', age)
    print('여성 비율', woman)
    print('남성 비율', man)

########################################################################
# TEMPLATES


def dashboard(request):
    orderTimeSheet = OrderTimeSheet()

    currentDate = orderTimeSheet.GetCurrentDate()
    currentDateWithoutTime = orderTimeSheet.GetCurrentDateWithoutTime()

    menuList = Menu.objects.filter(~Q(store__type=STORE_TYPE_PROMOTION)).order_by(
        '-status', '-store__status', '-current_stock', 'store__name')
    storeList = Store.objects.filter(
        ~Q(type=STORE_TYPE_PROMOTION) &
        ~Q(name__contains='잇플')
    ).annotate(
        currentStock=Sum('menu__current_stock')
    ).order_by('-currentStock')

    totalUser = User.objects.all()
    totalUserIncrease = totalUser.filter(
        create_date__gte=currentDateWithoutTime).count()

    totalOrder = Order.objects.filter(
        Q(payment_status=EATPLE_ORDER_STATUS_PAID) |
        Q(payment_status=EATPLE_ORDER_STATUS_CANCELLED)).count()

    dailyOrder = Order.objects.filter(
        Q(payment_status=EATPLE_ORDER_STATUS_PAID) &
        Q(pickup_time__gte=currentDateWithoutTime.replace(hour=0, minute=0)),
    )
    dailyOrderPrev = Order.objects.filter(
        Q(payment_status=EATPLE_ORDER_STATUS_PAID) &
        Q(pickup_time__gte=currentDateWithoutTime.replace(
            hour=0, minute=0) - datetime.timedelta(days=1)) &
        Q(pickup_time__lte=currentDateWithoutTime.replace(
            hour=0, minute=0) - datetime.timedelta(days=1))
    )

    orderChart = getOrderChart(orderTimeSheet, False)
    orderChartStaff = getOrderChart(orderTimeSheet, True)
    menuStockChart = getMenuStockChart(menuList)

    areaDataList = orderChart['data'].split(',')

    # userActive = getUserActive()
    # showActiveStatus(orderTimeSheet)
    # print('부탁하기된 주문수', getOrderDelegated())
    # userPersenalData()

    log = LogEntry.objects.all()

    return render(request, 'dashboard/dashboard.html', {
        'log': log[:5],
        'currentDate': '{}'.format(currentDate.strftime(
            '%Y년 %-m월 %-d일 %p %-I시 %-M분 %S초').replace('AM', '오전').replace('PM', '오후')),
        'menus': menuList,

        'storesOrderByPrevPrevMonth': sorted(storeList, key=(lambda i: -i.getPrevPrevMonthStock()[0])),
        'storesOrderByPrevMonth': sorted(storeList, key=(lambda i: -i.getPrevMonthStock()[0])),
        'stores': sorted(storeList, key=(lambda i: -i.getMontlyStock()[0])),

        'storesLunch': filter(lambda i: i.getLucnhCurrentStock() > 0, sorted(storeList, key=(lambda i: -i.getLucnhCurrentStock()))),
        'storesDinner': filter(lambda i: i.getDinnerCurrentStock() > 0, sorted(storeList, key=(lambda i: -i.getDinnerCurrentStock()))),

        'totalStockIncrease': dailyOrder.count() - dailyOrderPrev.count(),
        'totalStock': dailyOrder.count(),

        'dinnerStockIncrease': dailyOrder.filter(menu__selling_time=SELLING_TIME_DINNER).count() - dailyOrderPrev.filter(menu__selling_time=SELLING_TIME_DINNER).count(),
        'dinnerStock': dailyOrder.filter(menu__selling_time=SELLING_TIME_DINNER).count(),

        'lunchStockIncrease': dailyOrder.filter(menu__selling_time=SELLING_TIME_LUNCH).count() - dailyOrderPrev.filter(menu__selling_time=SELLING_TIME_LUNCH).count(),
        'lunchStock': dailyOrder.filter(menu__selling_time=SELLING_TIME_LUNCH).count(),

        'totalUserIncrease': totalUserIncrease,
        'totalUser': totalUser.count(),

        'totalOrder': totalOrder,

        'areaLabel': orderChart['label'],
        'areaData': orderChart['data'],
        'areaDataStaff': orderChartStaff['data'],
    })


def sales(request):
    orderTimeSheet = OrderTimeSheet()

    currentDate = orderTimeSheet.GetCurrentDate()
    currentDateWithoutTime = orderTimeSheet.GetCurrentDateWithoutTime()

    menuList = Menu.objects.filter(~Q(store__type=STORE_TYPE_PROMOTION)).order_by(
        '-status', '-store__status', '-current_stock', 'store__name')
    storeList = Store.objects.filter(
        ~Q(type=STORE_TYPE_PROMOTION) & ~Q(name__contains='잇플'))

    totalUser = User.objects.all()
    totalUserIncrease = totalUser.filter(
        create_date__gte=currentDateWithoutTime).count()

    totalOrder = Order.objects.filter(
        Q(payment_status=EATPLE_ORDER_STATUS_PAID) |
        Q(payment_status=EATPLE_ORDER_STATUS_CANCELLED)).count()

    dailyOrder = Order.objects.filter(
        Q(payment_status=EATPLE_ORDER_STATUS_PAID) &
        Q(pickup_time__gte=currentDateWithoutTime.replace(hour=0, minute=0)),
    )
    dailyOrderPrev = Order.objects.filter(
        Q(payment_status=EATPLE_ORDER_STATUS_PAID) &
        Q(pickup_time__gte=currentDateWithoutTime.replace(
            hour=0, minute=0) - datetime.timedelta(days=1)) &
        Q(pickup_time__lte=currentDateWithoutTime.replace(
            hour=0, minute=0) - datetime.timedelta(days=1))
    )

    orderChart = getOrderChart(orderTimeSheet)

    prevWAS = getWAS(orderTimeSheet)
    WAS = getWAS(orderTimeSheet)

    areaDataList = orderChart['data'].split(',')
    prevTotalStock = int(areaDataList[len(areaDataList)-2])
    totalStock = 0
    for menu in menuList:
        totalStock += menu.current_stock

    return render(request, 'dashboard/sales/sales.html', {
        'currentDate': '{}'.format(currentDate.strftime(
            '%Y년 %-m월 %-d일 %p %-I시 %-M분 %S초').replace('AM', '오전').replace('PM', '오후')),
        'menus': menuList,
        'stores': storeList,

        'WASIncrease': WAS - prevWAS,
        'WAS': WAS,

        'totalStockIncrease': dailyOrder.count() - dailyOrderPrev.count(),
        'totalStock': dailyOrder.count(),

        'dinnerStockIncrease': dailyOrder.filter(menu__selling_time=SELLING_TIME_DINNER).count() - dailyOrderPrev.filter(menu__selling_time=SELLING_TIME_DINNER).count(),
        'dinnerStock': dailyOrder.filter(menu__selling_time=SELLING_TIME_DINNER).count(),

        'lunchStockIncrease': dailyOrder.filter(menu__selling_time=SELLING_TIME_LUNCH).count() - dailyOrderPrev.filter(menu__selling_time=SELLING_TIME_LUNCH).count(),
        'lunchStock': dailyOrder.filter(menu__selling_time=SELLING_TIME_LUNCH).count(),


        'totalOrder': totalOrder,
    })


def sales_menulist(request):
    orderTimeSheet = OrderTimeSheet()

    currentDate = orderTimeSheet.GetCurrentDate()
    currentDateWithoutTime = orderTimeSheet.GetCurrentDateWithoutTime()

    menuList = Menu.objects.filter(~Q(store__type=STORE_TYPE_PROMOTION)).order_by(
        '-status', '-store__status', '-current_stock', 'store__name')
    storeList = Store.objects.filter(
        ~Q(type=STORE_TYPE_PROMOTION) & ~Q(name__contains='잇플'))

    totalUser = User.objects.all()
    totalUserIncrease = totalUser.filter(
        create_date__gte=currentDateWithoutTime).count()

    totalOrder = Order.objects.filter(
        Q(payment_status=EATPLE_ORDER_STATUS_PAID) |
        Q(payment_status=EATPLE_ORDER_STATUS_CANCELLED)).count()

    dailyOrder = Order.objects.filter(
        Q(payment_status=EATPLE_ORDER_STATUS_PAID) &
        Q(pickup_time__gte=currentDateWithoutTime.replace(hour=0, minute=0)),
    )
    dailyOrderPrev = Order.objects.filter(
        Q(payment_status=EATPLE_ORDER_STATUS_PAID) &
        Q(pickup_time__gte=currentDateWithoutTime.replace(
            hour=0, minute=0) - datetime.timedelta(days=1)) &
        Q(pickup_time__lte=currentDateWithoutTime.replace(
            hour=0, minute=0) - datetime.timedelta(days=1))
    )

    orderChart = getOrderChart(orderTimeSheet)

    prevWAS = getWAS(orderTimeSheet)
    WAS = getWAS(orderTimeSheet)

    areaDataList = orderChart['data'].split(',')

    return render(request, 'dashboard/sales/sales_menulist.html', {
        'currentDate': '{}'.format(currentDate.strftime(
            '%Y년 %-m월 %-d일 %p %-I시 %-M분 %S초').replace('AM', '오전').replace('PM', '오후')),
        'menus': menuList,
        'stores': storeList,

        'WASIncrease': WAS - prevWAS,
        'WAS': WAS,

        'totalStockIncrease': dailyOrder.count() - dailyOrderPrev.count(),
        'totalStock': dailyOrder.count(),

        'dinnerStockIncrease': dailyOrder.filter(menu__selling_time=SELLING_TIME_DINNER).count() - dailyOrderPrev.filter(menu__selling_time=SELLING_TIME_DINNER).count(),
        'dinnerStock': dailyOrder.filter(menu__selling_time=SELLING_TIME_DINNER).count(),

        'lunchStockIncrease': dailyOrder.filter(menu__selling_time=SELLING_TIME_LUNCH).count() - dailyOrderPrev.filter(menu__selling_time=SELLING_TIME_LUNCH).count(),
        'lunchStock': dailyOrder.filter(menu__selling_time=SELLING_TIME_LUNCH).count(),


        'totalOrder': totalOrder,
    })


def error404(request):
    return render(request, '404.html', {})
