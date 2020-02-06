from django.shortcuts import render

# Models
from eatple_app.models import *

# Define
from eatple_app.define import *

########################################################################
# METHOD
def replaceRight(original, old, new, count_right):
    repeat=0
    text = original
    
    count_find = original.count(old)
    if count_right > count_find : # 바꿀 횟수가 문자열에 포함된 old보다 많다면
        repeat = count_find # 문자열에 포함된 old의 모든 개수(count_find)만큼 교체한다
    else :
        repeat = count_right # 아니라면 입력받은 개수(count)만큼 교체한다

    for _ in range(repeat):
        find_index = text.rfind(old) # 오른쪽부터 index를 찾기위해 rfind 사용
        text = text[:find_index] + new + text[find_index+1:]
    
    return text

def getOrderChartDataLabel(currentDate):
    currentDateWithoutTime = currentDate.replace(
        hour=0, minute=0, second=0, microsecond=0)
    
    deadline = currentDateWithoutTime + datetime.timedelta(hours=16, minutes=20)

    if(currentDate <= deadline):
        currentDateWithoutTime = currentDateWithoutTime
    else:
        currentDateWithoutTime = currentDateWithoutTime + datetime.timedelta(days=1)
    
    areaLabel = ""
    
    for i in range(14):
        checkData = currentDateWithoutTime + datetime.timedelta(days=-(13 - i))
        
        areaLabel += "{},".format(checkData.strftime(
                '%-m월 %-d일').replace('AM', '오전').replace('PM', '오후'))
    
    return replaceRight(areaLabel, ",", "", 1)

def getOrderChartData(currentDate):    
    currentDateWithoutTime = currentDate.replace(
        hour=0, minute=0, second=0, microsecond=0)
    
    deadline = currentDateWithoutTime + datetime.timedelta(hours=16, minutes=20)

    if(currentDate <= deadline):
        currentDateWithoutTime = currentDateWithoutTime
    else:
        currentDateWithoutTime = currentDateWithoutTime + datetime.timedelta(days=1)
        
    areaData = ""
        
    for i in range(14):
        checkData = currentDateWithoutTime + datetime.timedelta(days=-(13 - i))

        # Prev Lunch Order Edit Time 16:30 ~ 시:25(~ 10:30)
        prevlunchOrderEditTimeStart = checkData + datetime.timedelta(hours=16, minutes=30, days=-1)

        # Next Lunch Order Edit Time 16:30 ~ 9:30(~ 10:30)
        nextlunchOrderEditTimeStart = checkData + datetime.timedelta(hours=16, minutes=30)
        
        areaData  += "{},".format((
            Order.objects.filter(
                Q(payment_date__gte=prevlunchOrderEditTimeStart) &
                Q(payment_date__lt=nextlunchOrderEditTimeStart) &
                Q(payment_status=IAMPORT_ORDER_STATUS_PAID)
            ).count())
        )
        
    return replaceRight(areaData, ",", "", 1)

def getDailyOrderChartDataLabel(currentDate):
    currentDateWithoutTime = currentDate.replace(
        hour=0, minute=0, second=0, microsecond=0)
    
    deadline = currentDateWithoutTime + datetime.timedelta(hours=16, minutes=20)

    if(currentDate <= deadline):
        startTime = currentDateWithoutTime + datetime.timedelta(hours=16, minutes=30, days=-1)
    else:
        startTime = currentDateWithoutTime + checkData + datetime.timedelta(hours=16, minutes=30)
    
    areaLabel = ""
    
    for i in range(24):
        checkStartTime = startTime + datetime.timedelta(hours=i)

        areaLabel += "{},".format(checkStartTime.strftime(
                '%-m월 %-d일 %p %-I시 %-M분 ~').replace('AM', '오전').replace('PM', '오후'))
    
    return replaceRight(areaLabel, ",", "", 1)

def getDailyOrderChartData(currentDate):    
    currentDateWithoutTime = currentDate.replace(
        hour=0, minute=0, second=0, microsecond=0)
    
    deadline = currentDateWithoutTime + datetime.timedelta(hours=16, minutes=20)

    if(currentDate <= deadline):
        startTime = currentDateWithoutTime + datetime.timedelta(hours=16, minutes=30, days=-1)
    else:
        startTime = currentDateWithoutTime + checkData + datetime.timedelta(hours=16, minutes=30)
        
    areaData = ""
        
    for i in range(24):
        checkStartTime = startTime + datetime.timedelta(hours=i)
        cehckEndTime = startTime + datetime.timedelta(hours=i+1)

        areaData  += "{},".format((
            Order.objects.filter(
                Q(payment_date__gte=checkStartTime) &
                Q(payment_date__lt=cehckEndTime) &
                Q(payment_status=IAMPORT_ORDER_STATUS_PAID)
            ).count())
        )
        
    return replaceRight(areaData, ",", "", 1)


def getMenuStockChartData(menuList):
    pieData = ""
        
    for menu in  menuList:
        pieData += "{},".format(menu.current_stock)
    
    return replaceRight(pieData, ",", "", 1)

def getMenuStockChartLabel(menuList):
    pieLabel = ""
        
    for menu in menuList:
        pieLabel += "{},".format(menu.name)
        
    return replaceRight(pieLabel, ",", "", 1)

def getDAU(currentDate):
    currentDateWithoutTime = currentDate.replace(
        hour=0, minute=0, second=0, microsecond=0)
    
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

def getWAU(currentDate):
    currentDateWithoutTime = currentDate.replace(
        hour=0, minute=0, second=0, microsecond=0)
    
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

def getMAU(currentDate):
    currentDateWithoutTime = currentDate.replace(
        hour=0, minute=0, second=0, microsecond=0)
    
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
    
########################################################################
# TEMPLATES
def base(request):
    currentDate = dateNowByTimeZone()
    currentDateWithoutTime = currentDate.replace(
    hour=0, minute=0, second=0, microsecond=0)
    
    menuList = Menu.objects.filter(~Q(store__type=STORE_TYPE_EVENT)).order_by('-status', '-store__status', '-current_stock','store__name')
    storeList = Store.objects.filter(~Q(type=STORE_TYPE_EVENT))

    totalUser = User.objects.all()
    totalUserIncrease = totalUser.filter(create_date__gte=currentDateWithoutTime).count()
    
    totalOrder = Order.objects.filter(
        Q(payment_status=IAMPORT_ORDER_STATUS_PAID) | 
        Q(payment_status=IAMPORT_ORDER_STATUS_CANCELLED)).count()
    totalOrderIncrease = totalUser.filter(create_date__gte=currentDateWithoutTime).count()
    
    areaLabel = getOrderChartDataLabel(currentDate)
    areaData = getOrderChartData(currentDate)
    
    areaDailyLabel = getDailyOrderChartDataLabel(currentDate)
    areaDailyData = getDailyOrderChartData(currentDate)

    pieLabel = getMenuStockChartLabel(menuList)
    pieData = getMenuStockChartData(menuList)

    prevDAU = getDAU(currentDate + datetime.timedelta(days=-1))
    prevWAU = getWAU(currentDate + datetime.timedelta(days=-1))
    prevMAU = getMAU(currentDate + datetime.timedelta(days=-1))
    
    DAU = getDAU(currentDate)
    WAU = getWAU(currentDate)
    MAU = getMAU(currentDate)
    
    areaDataList = areaData.split(",")
    prevTotalStock = int(areaDataList[len(areaDataList)-2])
    totalStock = 0
    for menu in menuList:
        totalStock += menu.current_stock
    
    
    return render(request, 'base/index.html', {
        'currentDate': "{}".format(currentDate.strftime(
                '%Y년 %-m월 %-d일 %p %-I시 %-M분 %S초').replace('AM', '오전').replace('PM', '오후')),
        'menus': menuList,
        'stores':storeList,

        'totalStockIncrease': totalStock - prevTotalStock,
        'totalStock': totalStock,
        
        'totalPriceIncrease': (totalStock * 6000) - (prevTotalStock * 6000),
        'totalPrice': totalStock * 6000,
        
        'totalUserIncrease': totalUserIncrease, 
        'totalUser': totalUser.count(),
        
        'totalOrder': totalOrder,
        
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
