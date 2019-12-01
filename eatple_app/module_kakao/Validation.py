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
        'action': "block",
        'label': "홈으로 돌아가기",
        'messageText': "로딩중..",
        'blockId': KAKAO_BLOCK_USER_HOME,
        'extra': {}
    },
]

def eatplePassValidation(user):
    orderManager = UserOrderManager(user)
    orderManager.orderPaidCheck()
    
    orderManager.availableOrderStatusUpdate();

    lunchPurchaed = orderManager.getAvailableLunchOrderPurchased().exists()
    dinnerPurchaced = orderManager.getAvailableDinnerOrderPurchased().exists()    
    
    KakaoForm = Kakao_SimpleForm()
    KakaoForm.SimpleForm_Init()

    for entryPoint in DEFAULT_QUICKREPLIES_MAP:
        KakaoForm.QuickReplies_Add(
            entryPoint['action'], 
            entryPoint['label'],
            entryPoint['messageText'], 
            entryPoint['blockId'], 
            entryPoint['extra'])

    if (lunchPurchaed and dinnerPurchaced):
        KakaoForm.SimpleText_Add(
            "오늘 하루, 잇플로 맛있는 식사를 즐겨주셔서 감사해요. 내일도 잇플과 함께 해주실거죠?"
        )
        return JsonResponse(KakaoForm.GetForm())
                
    elif (lunchPurchaed):
        KakaoForm.SimpleText_Add(
            "이미 점심 주문을 해주셨네요!\n내일 다시 잇플과 함께해주세요."
        )
        return JsonResponse(KakaoForm.GetForm())
    
    elif (dinnerPurchaced):
        KakaoForm.SimpleText_Add(
            "이미 저녁 주문을 해주셨네요!\n곧 있을 내일 점심 주문시간에 잇플과 다시 함께해주세요."
        )
        return JsonResponse(KakaoForm.GetForm())
        

    return None


def partnerValidation(KakaoPayload):
    try:
        app_user_id = KakaoPayload.user_properties['app_user_id']
        try:
            partner = Partner.objects.get(app_user_id=app_user_id)
            return partner
        except Partner.DoesNotExist:
            return None
    except (TypeError, AttributeError, KeyError):
        return None

def userValidation(KakaoPayload):
    try:
        app_user_id = KakaoPayload.user_properties['app_user_id']
        try:
            user = User.objects.get(app_user_id=app_user_id)
            return user
        except User.DoesNotExist:
            return None
    except (TypeError, AttributeError, KeyError):
        return None


def menuValidation(KakaoPayload):
    try:
        menu_id = KakaoPayload.dataActionExtra[KAKAO_PARAM_MENU_ID]
        try:
            menu = Menu.objects.get(menu_id=menu_id)
            return menu
        except Menu.DoesNotExist:
            return None
    except (TypeError, AttributeError, KeyError):
        return None
    
    
def storeValidation(KakaoPayload):
    try:
        store_id = KakaoPayload.dataActionExtra[KAKAO_PARAM_STORE_ID]
        try:
            store = Store.objects.get(store_id=store_id)
            return store
        except Store.DoesNotExist:
            return None
    except (TypeError, AttributeError, KeyError):
        return None


def orderValidation(KakaoPayload):
    try:
        order_id = KakaoPayload.dataActionExtra[KAKAO_PARAM_ORDER_ID]
        try:
            order = Order.objects.get(order_id=order_id)            
            return order
        except Order.DoesNotExist:
            return None
    except (TypeError, AttributeError, KeyError):
        return None

    
def pickupTimeValidation(KakaoPayload):
    try:
        pickupTime = KakaoPayload.dataActionExtra[KAKAO_PARAM_PICKUP_TIME]
        return pickupTime
    except (TypeError, AttributeError, KeyError):
        return None


def prevBlockValidation(KakaoPayload):
    try:
        prev_block_id = KakaoPayload.dataActionExtra[KAKAO_PARAM_PREV_BLOCK_ID]
        return prev_block_id
    except (TypeError, AttributeError, KeyError):
        return None
