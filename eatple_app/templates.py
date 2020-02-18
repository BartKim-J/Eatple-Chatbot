from django.shortcuts import render

# Models
from eatple_app.models import *

# Define
from eatple_app.define import *

########################################################################
# METHOD

WEEKDAY = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']


def replaceRight(original, old, new, count_right):
    repeat = 0
    text = original

    count_find = original.count(old)
    if count_right > count_find:  # 바꿀 횟수가 문자열에 포함된 old보다 많다면
        repeat = count_find  # 문자열에 포함된 old의 모든 개수(count_find)만큼 교체한다
    else:
        repeat = count_right  # 아니라면 입력받은 개수(count)만큼 교체한다

    for _ in range(repeat):
        find_index = text.rfind(old)  # 오른쪽부터 index를 찾기위해 rfind 사용
        text = text[:find_index] + new + text[find_index+1:]

    return text


def getOrderChartDataLabel(orderTimeSheet):
    currentDate = orderTimeSheet.GetCurrentDate()
    currentDateWithoutTime = orderTimeSheet.GetCurrentDateWithoutTime()

    deadline = orderTimeSheet.GetInitialCountTime()

    if(currentDate < deadline):
        currentDateWithoutTime = currentDateWithoutTime
    else:
        currentDateWithoutTime = currentDateWithoutTime + \
            datetime.timedelta(days=1)

    areaLabel = ""

    for i in range(21):
        checkData = currentDateWithoutTime + datetime.timedelta(days=-(20 - i))

        prevLunchOrderEditTimeStart = checkData + \
            datetime.timedelta(hours=16, minutes=30, days=-1)
        nextLunchOrderEditTimeStart = checkData + \
            datetime.timedelta(hours=16, minutes=30)

        if(prevLunchOrderEditTimeStart.strftime('%A') == 'Friday' and
           nextLunchOrderEditTimeStart.strftime('%A') == 'Saturday'):
            pass
        elif(prevLunchOrderEditTimeStart.strftime('%A') == 'Saturday' and
             nextLunchOrderEditTimeStart.strftime('%A') == 'Sunday'):
            pass
        else:
            areaLabel += "{} {},".format(checkData.strftime(
                '%-m월 %-d일').replace('AM', '오전').replace('PM', '오후'),
                WEEKDAY[checkData.weekday()])

    return replaceRight(areaLabel, ",", "", 1)


def getOrderChartData(orderTimeSheet):
    currentDate = orderTimeSheet.GetCurrentDate()
    currentDateWithoutTime = orderTimeSheet.GetCurrentDateWithoutTime()

    deadline = orderTimeSheet.GetInitialCountTime()

    if(currentDate < deadline):
        currentDateWithoutTime = currentDateWithoutTime
    else:
        currentDateWithoutTime = currentDateWithoutTime + \
            datetime.timedelta(days=1)

    areaData = ""

    for i in range(21):
        checkData = currentDateWithoutTime + datetime.timedelta(days=-(20 - i))

        prevLunchOrderEditTimeStart = checkData + \
            datetime.timedelta(hours=16, minutes=30, days=-1)
        nextLunchOrderEditTimeStart = checkData + \
            datetime.timedelta(hours=16, minutes=30)

        if(prevLunchOrderEditTimeStart.strftime('%A') == 'Friday' and
           nextLunchOrderEditTimeStart.strftime('%A') == 'Saturday'):
            pass
        elif(prevLunchOrderEditTimeStart.strftime('%A') == 'Saturday' and
             nextLunchOrderEditTimeStart.strftime('%A') == 'Sunday'):
            pass
        else:
            areaData += "{},".format((
                Order.objects.filter(
                    Q(payment_date__gte=prevLunchOrderEditTimeStart) &
                    Q(payment_date__lt=nextLunchOrderEditTimeStart) &
                    Q(payment_status=IAMPORT_ORDER_STATUS_PAID)
                ).count())
            )

    return replaceRight(areaData, ",", "", 1)


def getDailyOrderChartDataLabel(orderTimeSheet):
    currentDate = orderTimeSheet.GetCurrentDate()
    currentDateWithoutTime = orderTimeSheet.GetCurrentDateWithoutTime()

    deadline = orderTimeSheet.GetInitialCountTime()

    if(currentDate < deadline):
        startTime = orderTimeSheet.GetPrevLunchOrderEditTimeStart()
    else:
        startTime = orderTimeSheet.GetNextLunchOrderEditTimeStart()

    areaLabel = ""

    for i in range(24):
        checkStartTime = startTime + datetime.timedelta(hours=i)

        areaLabel += "{},".format(checkStartTime.strftime(
            '%-m월 %-d일 %p %-I시 %-M분 ~').replace('AM', '오전').replace('PM', '오후'))

    return replaceRight(areaLabel, ",", "", 1)


def getDailyOrderChartData(orderTimeSheet):
    currentDate = orderTimeSheet.GetCurrentDate()
    currentDateWithoutTime = orderTimeSheet.GetCurrentDateWithoutTime()

    deadline = orderTimeSheet.GetInitialCountTime()

    if(currentDate < deadline):
        startTime = orderTimeSheet.GetPrevLunchOrderEditTimeStart()
    else:
        startTime = orderTimeSheet.GetNextLunchOrderEditTimeStart()

    areaData = ""

    for i in range(24):
        checkStartTime = startTime + datetime.timedelta(hours=i)
        cehckEndTime = startTime + datetime.timedelta(hours=i+1)

        areaData += "{},".format((
            Order.objects.filter(
                Q(payment_date__gte=checkStartTime) &
                Q(payment_date__lt=cehckEndTime) &
                Q(payment_status=IAMPORT_ORDER_STATUS_PAID)
            ).count())
        )

    return replaceRight(areaData, ",", "", 1)


def getMenuStockChartData(menuList):
    pieData = ""

    menuList = menuList.filter(Q(current_stock__gte=1) & Q(
        status=OC_OPEN) & Q(store__status=OC_OPEN))

    for menu in menuList:
        pieData += "{},".format(menu.current_stock)

    return replaceRight(pieData, ",", "", 1)


def getMenuStockChartLabel(menuList):
    pieLabel = ""

    menuList = menuList.filter(Q(current_stock__gte=1) & Q(
        status=OC_OPEN) & Q(store__status=OC_OPEN))

    for menu in menuList:
        pieLabel += "{},".format(menu.name)

    return replaceRight(pieLabel, ",", "", 1)


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
        datetime.timedelta(hours=16, minutes=30, days=-1)
    nextLunchOrderEditTimeStart = currentDateWithoutTime + \
        datetime.timedelta(hours=16, minutes=30)

    totalPickuped = Order.objects.filter(
        Q(payment_status=IAMPORT_ORDER_STATUS_PAID) &
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
        datetime.timedelta(hours=16, minutes=30, days=-1)
    nextLunchOrderEditTimeStart = currentDateWithoutTime + \
        datetime.timedelta(hours=16, minutes=30)

    orderFailed = Order.objects.filter(
        Q(payment_status=IAMPORT_ORDER_STATUS_FAILED) &
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
            Q(payment_status=IAMPORT_ORDER_STATUS_PAID) |
            Q(payment_status=IAMPORT_ORDER_STATUS_CANCELLED) |
            Q(payment_status=IAMPORT_ORDER_STATUS_FAILED) |
            Q(payment_status=IAMPORT_ORDER_STATUS_NOT_PUSHED) |
            Q(payment_status=IAMPORT_ORDER_STATUS_READY)
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
            Q(payment_status=IAMPORT_ORDER_STATUS_PAID) |
            Q(payment_status=IAMPORT_ORDER_STATUS_CANCELLED) |
            Q(payment_status=IAMPORT_ORDER_STATUS_FAILED) |
            Q(payment_status=IAMPORT_ORDER_STATUS_NOT_PUSHED) |
            Q(payment_status=IAMPORT_ORDER_STATUS_READY)
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
            Q(payment_status=IAMPORT_ORDER_STATUS_PAID) |
            Q(payment_status=IAMPORT_ORDER_STATUS_CANCELLED) |
            Q(payment_status=IAMPORT_ORDER_STATUS_FAILED) |
            Q(payment_status=IAMPORT_ORDER_STATUS_NOT_PUSHED) |
            Q(payment_status=IAMPORT_ORDER_STATUS_READY)
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
            Q(payment_status=IAMPORT_ORDER_STATUS_PAID) |
            Q(payment_status=IAMPORT_ORDER_STATUS_CANCELLED) |
            Q(payment_status=IAMPORT_ORDER_STATUS_FAILED) |
            Q(payment_status=IAMPORT_ORDER_STATUS_NOT_PUSHED) |
            Q(payment_status=IAMPORT_ORDER_STATUS_READY)
        )
    ).values_list("store_id")

    WAS = list(set(WAS))

    return len(WAS)

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
        Q(payment_status=IAMPORT_ORDER_STATUS_PAID) |
        Q(payment_status=IAMPORT_ORDER_STATUS_CANCELLED)).count()

    totalOrderIncrease = totalUser.filter(
        create_date__gte=currentDateWithoutTime).count()

    areaLabel = getOrderChartDataLabel(orderTimeSheet)
    areaData = getOrderChartData(orderTimeSheet)

    areaDailyLabel = getDailyOrderChartDataLabel(orderTimeSheet)
    areaDailyData = getDailyOrderChartData(orderTimeSheet)

    pieLabel = getMenuStockChartLabel(menuList)
    pieData = getMenuStockChartData(menuList)

    prevDAU = getDAU(orderTimeSheet)
    prevWAU = getWAU(orderTimeSheet)
    prevMAU = getMAU(orderTimeSheet)

    DAU = getDAU(orderTimeSheet)
    WAU = getWAU(orderTimeSheet)
    MAU = getMAU(orderTimeSheet)

    areaDataList = areaData.split(",")
    prevTotalStock = int(areaDataList[len(areaDataList)-2])
    totalStock = 0
    for menu in menuList:
        totalStock += menu.current_stock

    totalPickuped = getTotalPickuped(orderTimeSheet)
    orderFailed = getOrderFailed(orderTimeSheet)

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

        'totalOrder': totalOrder,
        'orderFailed': orderFailed,

        'areaDailyLabel': areaDailyLabel,
        'areaDailyData': areaDailyData,

        'areaLabel': areaLabel,
        'areaData': areaData,

        'pieLabel': pieLabel,
        'pieData': pieData,

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
        Q(payment_status=IAMPORT_ORDER_STATUS_PAID) |
        Q(payment_status=IAMPORT_ORDER_STATUS_CANCELLED)).count()

    totalOrderIncrease = totalUser.filter(
        create_date__gte=currentDateWithoutTime).count()

    areaData = getOrderChartData(orderTimeSheet)

    prevWAS = getWAS(orderTimeSheet)

    WAS = getWAS(orderTimeSheet)

    areaDataList = areaData.split(",")
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
        Q(payment_status=IAMPORT_ORDER_STATUS_PAID) |
        Q(payment_status=IAMPORT_ORDER_STATUS_CANCELLED)).count()

    totalOrderIncrease = totalUser.filter(
        create_date__gte=currentDateWithoutTime).count()

    areaData = getOrderChartData(orderTimeSheet)

    prevWAS = getWAS(orderTimeSheet)

    WAS = getWAS(orderTimeSheet)

    areaDataList = areaData.split(",")
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
