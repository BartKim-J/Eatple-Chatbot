# Django Library
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

# Models
from eatple_app.models import *

# Define
from eatple_app.define import *

# Modules
from eatple_app.module_kakao.ReponseForm import *
from eatple_app.module_kakao.RequestForm import *

# View-System
from eatple_app.views_system.debugger import *


from eatple_app.views import *

DEFAULT_QUICKREPLIES_MAP = [
    {
        'action': 'block',
        'label': '홈으로 돌아가기',
        'messageText': '로딩중..',
        'blockId': KAKAO_BLOCK_USER_HOME,
        'extra': {}
    },
    {
        'action': 'block',
        'label': '잇플패스 확인하기',
        'messageText': '로딩중..',
        'blockId': KAKAO_BLOCK_USER_EATPLE_PASS,
        'extra': {}
    },
]

def sellingTimeCheck():
    currentDate = dateNowByTimeZone()
    currentDateWithoutTime = currentDate.replace(
        hour=0, minute=0, second=0, microsecond=0)

    # Time QA DEBUG
    #currentDate = currentDate.replace(hour=9, minute=31, second=0, microsecond=0)
    #currentDateWithoutTime = currentDate.replace(hour=0, minute=0, second=0, microsecond=0)

    # DEBUG
    #return SELLING_TIME_LUNCH

    # Prev Lunch Order Time 16:30 ~ 10:30
    prevlunchOrderTimeStart = currentDateWithoutTime + \
        datetime.timedelta(hours=16, minutes=30, days=-1)
    prevlunchOrderTimeEnd = currentDateWithoutTime + \
        datetime.timedelta(hours=10, minutes=30)

    # Dinner Order Time 10:30 ~ 16:30
    dinnerOrderTimeStart = currentDateWithoutTime + \
        datetime.timedelta(hours=10, minutes=30)
    dinnerOrderTimeEnd = currentDateWithoutTime + \
        datetime.timedelta(hours=16, minutes=30)

    # Next Lunch Order Time 16:30 ~ 10:30
    nextlunchOrderTimeStart = currentDateWithoutTime + \
        datetime.timedelta(hours=16, minutes=30)
    nextlunchOrderTimeEnd = currentDateWithoutTime + \
        datetime.timedelta(hours=10, minutes=30, days=1)

    if(dinnerOrderTimeStart <= currentDate) and (currentDate <= dinnerOrderTimeEnd):
        return SELLING_TIME_DINNER
    elif(prevlunchOrderTimeStart < currentDate) and (currentDate < prevlunchOrderTimeEnd):
        return SELLING_TIME_LUNCH
    elif(nextlunchOrderTimeStart < currentDate) and (currentDate < nextlunchOrderTimeEnd):
        return SELLING_TIME_LUNCH
    else:
        return None

def weekendTimeCheck():

    currentDate = dateNowByTimeZone()
    currentDateWithoutTime = currentDate.replace(
        hour=0, minute=0, second=0, microsecond=0)

    # Time QA DEBUG
    #currentDate = currentDate.replace(day=19, hour=9, minute=28, second=0, microsecond=0)
    #currentDateWithoutTime = currentDate.replace(hour=0, minute=0, second=0, microsecond=0)

    # DEBUG
    #return False

    closedDateStart = currentDateWithoutTime + \
        datetime.timedelta(hours=10, minutes=30)
    closedDateEnd = currentDateWithoutTime + \
        datetime.timedelta(hours=16, minutes=30)

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
     
    # Time QA DEBUG
    #currentDate = currentDate.replace(month=1, day=26, hour=9, minute=28, second=0, microsecond=0)
    #currentDateWithoutTime = currentDate.replace(hour=0, minute=0, second=0, microsecond=0)
    #print(currentDate)
    
    for vacation in vacationMap:
        closedDateStart = currentDate.replace(month=vacation['from_month'], day=vacation['from_days'], hour=0, minute=0, second=0, microsecond=0)
        closedDateEnd = currentDate.replace(
            month=vacation['to_month'], day=vacation['to_days'], hour=23, minute=59, second=59, microsecond=0)

        if(closedDateStart <= currentDate and currentDate <= closedDateEnd):
            return True
    
    return False
    

def eatplePassValidation(user):
    orderManager = UserOrderManager(user)
    orderManager.orderPaidCheck()
    
    orderManager.availableOrderStatusUpdate();

    lunchPurchaed = orderManager.getAvailableLunchOrderPurchased().exists()
    dinnerPurchaced = orderManager.getAvailableDinnerOrderPurchased().exists()    
    
    kakaoForm = KakaoForm()

    kakaoForm.QuickReplies_AddWithMap(DEFAULT_QUICKREPLIES_MAP)

    if (lunchPurchaed and dinnerPurchaced):
        kakaoForm.SimpleText_Add(
            '아직 사용하지 않은 잇플패스가 있어요.\n발급된 잇플패스를 먼저 사용해주세요.'
        )
        return JsonResponse(kakaoForm.GetForm())
                
    elif (lunchPurchaed):
        kakaoForm.SimpleText_Add(
            '아직 사용하지 않은 잇플패스가 있어요.\n발급된 잇플패스를 먼저 사용해주세요.'
        )
        return JsonResponse(kakaoForm.GetForm())
    
    elif (dinnerPurchaced):
        kakaoForm.SimpleText_Add(
            '아직 사용하지 않은 잇플패스가 있어요.\n발급된 잇플패스를 먼저 사용해주세요.'
        )
        return JsonResponse(kakaoForm.GetForm())
        

    return None

def partnerValidation(kakaoPayload):
    try:
        app_user_id = kakaoPayload.user_properties['app_user_id']
        try:
            partner = Partner.objects.get(app_user_id=app_user_id)
            return partner
        except Partner.DoesNotExist:
            return None
    except (TypeError, AttributeError, KeyError):
        return None

def userValidation(kakaoPayload):
    try:
        app_user_id = kakaoPayload.user_properties['app_user_id']
        try:
            user = User.objects.get(app_user_id=app_user_id)
            return user
        except User.DoesNotExist:
            return None
    except (TypeError, AttributeError, KeyError):
        return None

def userLocationValidation(user):
    try:
        try:
            location = Location.objects.get(user=user)
        except AttributeError:
            location = Location.objects.filter(user=user)[:1]
            
        return location
    except Location.DoesNotExist:
        return None
    
def menuValidation(kakaoPayload):
    try:
        menu_id = kakaoPayload.dataActionExtra[KAKAO_PARAM_MENU_ID]
        try:
            menu = Menu.objects.get(menu_id=menu_id)
            return menu
        except Menu.DoesNotExist:
            return None
    except (TypeError, AttributeError, KeyError):
        return None
    
def storeValidation(kakaoPayload):
    try:
        store_id = kakaoPayload.dataActionExtra[KAKAO_PARAM_STORE_ID]
        try:
            store = Store.objects.get(store_id=store_id)
            return store
        except Store.DoesNotExist:
            return None
    except (TypeError, AttributeError, KeyError):
        return None

def orderValidation(kakaoPayload):
    try:
        order_id = kakaoPayload.dataActionExtra[KAKAO_PARAM_ORDER_ID]
        try:
            order = Order.objects.get(order_id=order_id)            
            return order
        except Order.DoesNotExist:
            return None
    except (TypeError, AttributeError, KeyError):
        return None

def pickupTimeValidation(kakaoPayload):
    try:
        pickupTime = kakaoPayload.dataActionExtra[KAKAO_PARAM_PICKUP_TIME]
        return pickupTime
    except (TypeError, AttributeError, KeyError):
        return None

def prevBlockValidation(kakaoPayload):
    try:
        prev_block_id = kakaoPayload.dataActionExtra[KAKAO_PARAM_PREV_BLOCK_ID]
        return prev_block_id
    except (TypeError, AttributeError, KeyError):
        return None
