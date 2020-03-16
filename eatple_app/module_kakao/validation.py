# Models
from eatple_app.models import *

# Define
from eatple_app.define import *


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
        if(USER_ID_DEBUG_MODE):
            app_user_id = DEBUG_USER_ID
        else:
            app_user_id = kakaoPayload.user_properties['app_user_id']
        try:
            user = User.objects.get(app_user_id=app_user_id)
            return user
        except User.DoesNotExist:
            return None
    except (TypeError, AttributeError, KeyError):
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
