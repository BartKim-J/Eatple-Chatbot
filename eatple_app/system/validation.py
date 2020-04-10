# Django Library
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

# Models
from eatple_app.models import *

# Define
from eatple_app.define import *

# Modules
from eatple_app.module_kakao.responseForm import *
from eatple_app.module_kakao.requestForm import *
from eatple_app.module_kakao.kakaoPay import *

# View-System
from eatple_app.views_system.debugger import *

from eatple_app.views import *

DEFAULT_QUICKREPLIES_MAP = [
    {
        'action': 'block',
        'label': '🏠  홈',
        'messageText': KAKAO_EMOJI_LOADING,
        'blockId': KAKAO_BLOCK_USER_HOME,
        'extra': {}
    },
    {
        'action': 'block',
        'label': '잇플패스 확인하기',
        'messageText': KAKAO_EMOJI_LOADING,
        'blockId': KAKAO_BLOCK_USER_EATPLE_PASS,
        'extra': {}
    },
]


def userLocationValidation(user):
    try:
        try:
            location = Location.objects.get(user=user)
        except AttributeError:
            location = Location.objects.filter(user=user)[:1]

        return location
    except Location.DoesNotExist:
        return None


def isB2BUser(user):
    try:
        B2BUser = UserB2B.objects.get(phone_number=user.phone_number)

        if(user.type != USER_TYPE_B2B or user.company == None or (user.company != Company.objects.get(id=int(B2BUser.company.id)))):
            user.company = Company.objects.get(id=int(B2BUser.company.id))
            user.type = USER_TYPE_B2B
            user.save()

        if(user.company.status != OC_OPEN):
            return False

        return True
    except UserB2B.DoesNotExist:
        user.company = None
        user.type = USER_TYPE_NORMAL
        user.save()
        return False

    return False


def sellingTimeCheck():
    # DEBUG
    if(VALIDATION_DEBUG_MODE):
        return SELLING_TIME_LUNCH

    orderTimeSheet = OrderTimeSheet()

    currentDate = orderTimeSheet.GetCurrentDate()

    # Prev Lunch Order Time
    prevLunchOrderTimeStart = orderTimeSheet.GetPrevLunchOrderEditTimeStart()
    prevLunchOrderTimeEnd = orderTimeSheet.GetPrevLunchOrderEditTimeEnd()

    # Dinner Order Time
    dinnerOrderTimeStart = orderTimeSheet.GetDinnerOrderEditTimeStart()
    dinnerOrderTimeEnd = orderTimeSheet.GetDinnerOrderTimeEnd()

    # Next Lunch Order Time
    nextLunchOrderTimeStart = orderTimeSheet.GetNextLunchOrderEditTimeStart()
    nextLunchOrderTimeEnd = orderTimeSheet.GetNextLunchOrderEditTimeEnd()

    if(prevLunchOrderTimeEnd < currentDate) and (currentDate < dinnerOrderTimeStart):
        return SELLING_TIME_DINNER
    elif(prevLunchOrderTimeStart < currentDate) and (currentDate < prevLunchOrderTimeEnd):
        return SELLING_TIME_LUNCH
    elif(nextLunchOrderTimeStart < currentDate) and (currentDate < nextLunchOrderTimeEnd):
        return SELLING_TIME_LUNCH
    elif(dinnerOrderTimeStart < currentDate) and (currentDate < dinnerOrderTimeEnd):
        return SELLING_TIME_DINNER
    else:
        return None


def weekendTimeCheck():
    orderTimeSheet = OrderTimeSheet()
    currentDate = orderTimeSheet.GetCurrentDate()
    currentDateWithoutTime = orderTimeSheet.GetCurrentDateWithoutTime()

    # DEBUG
    if(VALIDATION_DEBUG_MODE):
        return False

    closedDateStart = orderTimeSheet.GetPrevLunchOrderTimeEnd()
    closedDateEnd = orderTimeSheet.GetNextLunchOrderEditTimeStart()

    if(currentDate.strftime('%A') == 'Friday'):
        if(currentDate >= closedDateStart):
            return True
        else:
            return False
    elif(currentDate.strftime('%A') == 'Saturday'):
        return True
    elif(currentDate.strftime('%A') == 'Sunday'):
        if(currentDate <= closedDateEnd):
            return True
        else:
            return False
    else:
        return False


def vacationTimeCheck():
    currentDate = dateNowByTimeZone()
    currentDateWithoutTime = currentDate.replace(
        hour=0, minute=0, second=0, microsecond=0)

    vacationMap = [
        {
            'from_month': 1,
            'from_days': 1,
            'to_month': 1,
            'to_days': 1
        },
        {
            'from_month': 1,
            'from_days': 24,
            'to_month': 1,
            'to_days': 27
        },
    ]

    for vacation in vacationMap:
        closedDateStart = currentDate.replace(
            month=vacation['from_month'], day=vacation['from_days'], hour=0, minute=0, second=0, microsecond=0)
        closedDateEnd = currentDate.replace(
            month=vacation['to_month'], day=vacation['to_days'], hour=23, minute=59, second=59, microsecond=0)

        if(closedDateStart <= currentDate and currentDate <= closedDateEnd):
            return True

    return False


def eatplePassValidation(user, kakaoPayload):
    orderManager = UserOrderManager(user)
    orderManager.orderPaidCheck()

    orderManager.availableOrderStatusUpdate()

    lunchPurchaed = orderManager.getAvailableLunchOrderPurchased().filter(
        ordersheet__user=user).exists()
    dinnerPurchaced = orderManager.getAvailableDinnerOrderPurchased().filter(
        ordersheet__user=user).exists()

    kakaoForm = KakaoForm()

    kakaoForm.QuickReplies_AddWithMap(DEFAULT_QUICKREPLIES_MAP)

    if (lunchPurchaed and dinnerPurchaced):
        return GET_EatplePass(kakaoPayload.request)

    elif (lunchPurchaed):
        return GET_EatplePass(kakaoPayload.request)

    elif (dinnerPurchaced):
        return GET_EatplePass(kakaoPayload.request)

    return None
