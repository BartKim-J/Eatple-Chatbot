from django.shortcuts import render

# Models
from eatple_app.models import *

# Define
from eatple_app.define import *

########################################################################
# METHOD

WEEKDAY = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']


def getOrderChart(orderTimeSheet):
    currentDate = orderTimeSheet.GetCurrentDate()
    currentDateWithoutTime = orderTimeSheet.GetCurrentDateWithoutTime()

    deadline = orderTimeSheet.GetInitialCountTime()

    if(currentDate < deadline):
        currentDateWithoutTime = currentDateWithoutTime
    else:
        currentDateWithoutTime = currentDateWithoutTime + \
            datetime.timedelta(days=1)

    label = ""
    data = ""

    for i in range(21):
        checkData = currentDateWithoutTime + datetime.timedelta(days=-(20 - i))

        prevLunchOrderEditTimeStart = checkData + \
            datetime.timedelta(hours=16, minutes=0, days=-1)
        nextLunchOrderEditTimeStart = checkData + \
            datetime.timedelta(hours=16, minutes=0)

        if(prevLunchOrderEditTimeStart.strftime('%A') == 'Friday' and
           nextLunchOrderEditTimeStart.strftime('%A') == 'Saturday'):
            pass
        elif(prevLunchOrderEditTimeStart.strftime('%A') == 'Saturday' and
             nextLunchOrderEditTimeStart.strftime('%A') == 'Sunday'):
            pass
        else:
            label += "{} {},".format(checkData.strftime(
                '%-m월 %-d일').replace('AM', '오전').replace('PM', '오후'),
                WEEKDAY[checkData.weekday()])

            data += "{},".format((
                Order.objects.filter(
                    Q(payment_date__gte=prevLunchOrderEditTimeStart) &
                    Q(payment_date__lt=nextLunchOrderEditTimeStart) &
                    Q(payment_status=EATPLE_ORDER_STATUS_PAID)
                ).count())
            )

    label = replaceRight(label, ",", "", 1)
    data = replaceRight(data, ",", "", 1)

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

    label = ""
    data = ""

    checkHours = 5
    minuteInterval = 5

    for i in range(int(60/minuteInterval) * checkHours):
        checkData = currentDateWithoutTime + \
            datetime.timedelta(
                days=0, hours=11, minutes=30 + (minuteInterval * i))

        startTime = checkData
        endTime = checkData + datetime.timedelta(minutes=minuteInterval)

        if(startTime >= currentDate):
            label += "픽업시간이 아님,"
        else:
            label += "{} ~ {},".format(startTime.strftime(
                '%p %-I시 %-M분').replace('AM', '오전').replace('PM', '오후'),
                endTime.strftime(
                '%p %-I시 %-M분').replace('AM', '오전').replace('PM', '오후')
            )

        data += "{},".format((
            Order.objects.filter(
                Q(pickup_complete_date__gte=startTime) &
                Q(pickup_complete_date__lt=endTime) &
                Q(payment_status=EATPLE_ORDER_STATUS_PAID) &
                Q(status=ORDER_STATUS_PICKUP_COMPLETED)
            ).count())
        )

    label = replaceRight(label, ",", "", 1)
    data = replaceRight(data, ",", "", 1)

    return {
        'label': label,
        'data': data
    }


def getDailyOrderChart(orderTimeSheet):
    currentDate = orderTimeSheet.GetCurrentDate()
    currentDateWithoutTime = orderTimeSheet.GetCurrentDateWithoutTime()

    deadline = orderTimeSheet.GetInitialCountTime()

    if(currentDate < deadline):
        startTime = orderTimeSheet.GetPrevLunchOrderEditTimeStart()
    else:
        startTime = orderTimeSheet.GetNextLunchOrderEditTimeStart()

    label = ""
    data = ""

    for i in range(24):
        checkStartTime = startTime + datetime.timedelta(hours=i)
        cehckEndTime = startTime + datetime.timedelta(hours=i+1)

        label += "{},".format(checkStartTime.strftime(
            '%-m월 %-d일 %p %-I시 %-M분 ~').replace('AM', '오전').replace('PM', '오후'))

        data += "{},".format((
            Order.objects.filter(
                Q(payment_date__gte=checkStartTime) &
                Q(payment_date__lt=cehckEndTime) &
                Q(payment_status=EATPLE_ORDER_STATUS_PAID)
            ).count())
        )

    label = replaceRight(label, ",", "", 1)
    data = replaceRight(data, ",", "", 1)

    return {
        'label': label,
        'data': data
    }


def getMenuStockChart(menuList):
    label = ""
    data = ""

    menuList = menuList.filter(Q(current_stock__gte=1) & Q(
        status=OC_OPEN) & Q(store__status=OC_OPEN))

    for menu in menuList:
        data += "{},".format(menu.current_stock)
        label += "{},".format(menu.name)

    data = replaceRight(data, ",", "", 1)
    label = replaceRight(label, ",", "", 1)

    return {
        'data': data,
        'label': label,
    }


def getTotalPickuped(orderTimeSheet):
    currentDate = orderTimeSheet.GetCurrentDate()
    currentDateWithoutTime = orderTimeSheet.GetCurrentDateWithoutTime()

    deadline = orderTimeSheet.GetInitialCountTime()

    if(currentDate < deadline):
        currentDateWithoutTime = currentDateWithoutTime
    else:
        currentDateWithoutTime = currentDateWithoutTime + \
            datetime.timedelta(days=1)

    prevLunchOrderEditTimeStart = currentDateWithoutTime + \
        datetime.timedelta(hours=16, minutes=0, days=-1)
    nextLunchOrderEditTimeStart = currentDateWithoutTime + \
        datetime.timedelta(hours=16, minutes=0)

    totalPickuped = Order.objects.filter(
        Q(payment_status=EATPLE_ORDER_STATUS_PAID) &
        Q(status=ORDER_STATUS_PICKUP_COMPLETED) &
        Q(payment_date__gte=prevLunchOrderEditTimeStart) &
        Q(payment_date__lt=nextLunchOrderEditTimeStart)
    ).count()

    return totalPickuped


def getOrderFailed(orderTimeSheet):
    currentDate = orderTimeSheet.GetCurrentDate()
    currentDateWithoutTime = orderTimeSheet.GetCurrentDateWithoutTime()

    deadline = orderTimeSheet.GetInitialCountTime()

    if(currentDate < deadline):
        currentDateWithoutTime = currentDateWithoutTime
    else:
        currentDateWithoutTime = currentDateWithoutTime + \
            datetime.timedelta(days=1)

    prevLunchOrderEditTimeStart = currentDateWithoutTime + \
        datetime.timedelta(hours=16, minutes=0, days=-1)
    nextLunchOrderEditTimeStart = currentDateWithoutTime + \
        datetime.timedelta(hours=16, minutes=0)

    orderFailed = Order.objects.filter(
        Q(payment_status=EATPLE_ORDER_STATUS_FAILED) &
        Q(payment_date__gte=prevLunchOrderEditTimeStart) &
        Q(payment_date__lt=nextLunchOrderEditTimeStart)
    ).count()

    return orderFailed


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
    ).values_list("ordersheet__user__app_user_id")

    DAU = list(set(DAU))

    return len(DAU)


def getWAU(orderTimeSheet):
    currentDate = orderTimeSheet.GetCurrentDate() + datetime.timedelta(days=-1)
    currentDateWithoutTime = orderTimeSheet.GetCurrentDateWithoutTime()

    WAUStartDate = currentDateWithoutTime + datetime.timedelta(days=-7)
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
    ).values_list("ordersheet__user__app_user_id")

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
    ).values_list("ordersheet__user__app_user_id")

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
    ).values_list("store_id")

    WAS = list(set(WAS))

    return len(WAS)


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
            NotAtive += 1

        elif(count == 1):
            InActive += 1

        elif(count >= 2):
            GetActive += 1

        elif(count >= 3):
            OnActive += 1

    data = {
        'userInService': userListInService.count(),
        'notActive': NotAtive,
        'inActive': InActive,
        'getActive': GetActive,
        'onActive': OnActive,
    }

    return data

########################################################################
# TEMPLATES


def dashboard(request):
    orderTimeSheet = OrderTimeSheet()

    currentDate = orderTimeSheet.GetCurrentDate()
    currentDateWithoutTime = orderTimeSheet.GetCurrentDateWithoutTime()

    menuList = Menu.objects.filter(~Q(store__type=STORE_TYPE_PROMOTION)).order_by(
        '-status', '-store__status', '-current_stock', 'store__name')
    storeList = Store.objects.filter(~Q(type=STORE_TYPE_PROMOTION))

    totalUser = User.objects.all()
    totalUserIncrease = totalUser.filter(
        create_date__gte=currentDateWithoutTime).count()

    totalOrder = Order.objects.filter(
        Q(payment_status=EATPLE_ORDER_STATUS_PAID) |
        Q(payment_status=EATPLE_ORDER_STATUS_CANCELLED)).count()

    totalOrderIncrease = totalUser.filter(
        create_date__gte=currentDateWithoutTime).count()

    orderChart = getOrderChart(orderTimeSheet)
    pickupTimeChart = getPickupTimeChart(orderTimeSheet)
    dailyOrderChart = getDailyOrderChart(orderTimeSheet)
    menuStockChart = getMenuStockChart(menuList)

    prevDAU = getDAU(orderTimeSheet)
    prevWAU = getWAU(orderTimeSheet)
    prevMAU = getMAU(orderTimeSheet)

    DAU = getDAU(orderTimeSheet)
    WAU = getWAU(orderTimeSheet)
    MAU = getMAU(orderTimeSheet)

    areaDataList = orderChart['data'].split(",")
    prevTotalStock = int(areaDataList[len(areaDataList)-2])
    totalStock = 0
    for menu in menuList:
        totalStock += menu.current_stock

    totalPickuped = getTotalPickuped(orderTimeSheet)
    orderFailed = getOrderFailed(orderTimeSheet)

    userActive = getUserActive()

    return render(request, 'dashboard/base.html', {
        'currentDate': "{}".format(currentDate.strftime(
            '%Y년 %-m월 %-d일 %p %-I시 %-M분 %S초').replace('AM', '오전').replace('PM', '오후')),
        'menus': menuList,
        'stores': storeList,

        'totalStockIncrease': totalStock - prevTotalStock,
        'totalStock': totalStock,

        'totalPickuped': totalPickuped,

        'totalPriceIncrease': (totalStock * 6000) - (prevTotalStock * 6000),
        'totalPrice': totalStock * 6000,

        'totalUserIncrease': totalUserIncrease,
        'totalUser': totalUser.count(),

        'userInService': userActive['userInService'],
        'notActive': userActive['notActive'],
        'inActive': userActive['inActive'],
        'getActive': userActive['getActive'],

        'totalOrder': totalOrder,
        'orderFailed': orderFailed,

        'areaDailyLabel':  dailyOrderChart['label'],
        'areaDailyData': dailyOrderChart['data'],

        'pickupChartLabel':  pickupTimeChart['label'],
        'pickupChartData': pickupTimeChart['data'],

        'areaLabel': orderChart['label'],
        'areaData': orderChart['data'],

        'pieLabel': menuStockChart['label'],
        'pieData': menuStockChart['data'],

        'DAU': DAU,
        'WAU': WAU,
        'MAU': MAU,

        'DAUIncrease': DAU - prevDAU,
        'WAUIncrease': WAU - prevWAU,
        'MAUIncrease': MAU - prevMAU,
    })


def sales_dashboard(request):
    orderTimeSheet = OrderTimeSheet()

    currentDate = orderTimeSheet.GetCurrentDate()
    currentDateWithoutTime = orderTimeSheet.GetCurrentDateWithoutTime()

    menuList = Menu.objects.filter(~Q(store__type=STORE_TYPE_PROMOTION)).order_by(
        '-status', '-store__status', '-current_stock', 'store__name')
    storeList = Store.objects.filter(~Q(type=STORE_TYPE_PROMOTION))

    totalUser = User.objects.all()
    totalUserIncrease = totalUser.filter(
        create_date__gte=currentDateWithoutTime).count()

    totalOrder = Order.objects.filter(
        Q(payment_status=EATPLE_ORDER_STATUS_PAID) |
        Q(payment_status=EATPLE_ORDER_STATUS_CANCELLED)).count()

    totalOrderIncrease = totalUser.filter(
        create_date__gte=currentDateWithoutTime).count()

    orderChart = getOrderChart(orderTimeSheet)

    prevWAS = getWAS(orderTimeSheet)

    WAS = getWAS(orderTimeSheet)

    areaDataList = orderChart['data'].split(",")
    prevTotalStock = int(areaDataList[len(areaDataList)-2])
    totalStock = 0
    for menu in menuList:
        totalStock += menu.current_stock

    totalPickuped = getTotalPickuped(orderTimeSheet)
    orderFailed = getOrderFailed(orderTimeSheet)

    return render(request, 'dashboard/sales_dashboard.html', {
        'currentDate': "{}".format(currentDate.strftime(
            '%Y년 %-m월 %-d일 %p %-I시 %-M분 %S초').replace('AM', '오전').replace('PM', '오후')),
        'menus': menuList,
        'stores': storeList,

        'WASIncrease': WAS - prevWAS,
        'WAS': WAS,

        'totalStockIncrease': totalStock - prevTotalStock,
        'totalStock': totalStock,

        'totalPickuped': totalPickuped,

        'totalOrder': totalOrder,
        'orderFailed': orderFailed,
    })


def sales_menulist(request):
    orderTimeSheet = OrderTimeSheet()

    currentDate = orderTimeSheet.GetCurrentDate()
    currentDateWithoutTime = orderTimeSheet.GetCurrentDateWithoutTime()

    menuList = Menu.objects.filter(~Q(store__type=STORE_TYPE_PROMOTION)).order_by(
        '-status', '-store__status', '-current_stock', 'store__name')
    storeList = Store.objects.filter(~Q(type=STORE_TYPE_PROMOTION))

    totalUser = User.objects.all()
    totalUserIncrease = totalUser.filter(
        create_date__gte=currentDateWithoutTime).count()

    totalOrder = Order.objects.filter(
        Q(payment_status=EATPLE_ORDER_STATUS_PAID) |
        Q(payment_status=EATPLE_ORDER_STATUS_CANCELLED)).count()

    totalOrderIncrease = totalUser.filter(
        create_date__gte=currentDateWithoutTime).count()

    orderChart = getOrderChart(orderTimeSheet)

    prevWAS = getWAS(orderTimeSheet)

    WAS = getWAS(orderTimeSheet)

    areaDataList = orderChart['data'].split(",")
    prevTotalStock = int(areaDataList[len(areaDataList)-2])
    totalStock = 0
    for menu in menuList:
        totalStock += menu.current_stock

    totalPickuped = getTotalPickuped(orderTimeSheet)
    orderFailed = getOrderFailed(orderTimeSheet)

    return render(request, 'dashboard/sales_menulist.html', {
        'currentDate': "{}".format(currentDate.strftime(
            '%Y년 %-m월 %-d일 %p %-I시 %-M분 %S초').replace('AM', '오전').replace('PM', '오후')),
        'menus': menuList,
        'stores': storeList,

        'WASIncrease': WAS - prevWAS,
        'WAS': WAS,

        'totalStockIncrease': totalStock - prevTotalStock,
        'totalStock': totalStock,

        'totalPickuped': totalPickuped,

        'totalOrder': totalOrder,
        'orderFailed': orderFailed,
    })


def error404(request):
    return render(request, '404.html', {})
