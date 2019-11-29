# System
import sys
import os

# Django Library
from django.conf import settings

# External Library
from datetime import datetime, timedelta, timezone
import requests
import json

import pytz


EATPLUS_HOST_URL = "http://eatple.com:8000"
VALUE_NOT_APPLICABLE = 'N/A'

# Eatplus App Global Defines
STRING_32 = 31
STRING_256 = 255

USE_TZ = settings.USE_TZ
TIME_ZONE = settings.TIME_ZONE

HOST_URL = EATPLUS_HOST_URL

NOT_APPLICABLE = VALUE_NOT_APPLICABLE
DEFAULT_OBJECT_ID = 1
DEFAULT_USER_ID = 2

# IMAGE DB PATH
PATH_IMG_DB = "STORE_DB/images"

# USER LENGTH
USER_NICKNAME_LENGTH = STRING_32
USER_ID_LENGTH = STRING_32
USER_ID_CODE_LENGTH = STRING_256

# PARTNER LENGTH
PARTNER_ID_CODE_LENGTH = STRING_256

# STRING LENGTH
STRING_LENGTH = STRING_256
WORD_LENGTH = STRING_32

# MENU
MANAGEMENT_CODE_DEFAULT = VALUE_NOT_APPLICABLE
MANAGEMENT_CODE_LENGTH = STRING_256

SELLING_TIME_LUNCH = 0
SELLING_TIME_DINNER = 1
SELLING_TIME_CATEGORY = [
    (SELLING_TIME_LUNCH, '점심'),
    (SELLING_TIME_DINNER, '저녁'),
]

# ORDERING
ORDER_STATUS_PAYMENT_WAIT = 0
ORDER_STATUS_PAYMENT_COMPLETED = 1
ORDER_STATUS_REFUND_WAIT = 2
ORDER_STATUS_REFUND_COMPLETED = 3
ORDER_STATUS_ORDER_CONFIRM_WAIT = 4
ORDER_STATUS_ORDER_CONFIRMED = 5
ORDER_STATUS_ORDER_CANCELED = 6
ORDER_STATUS_ORDER_EXPIRED = 7
ORDER_STATUS_PICKUP_PREPARE = 8
ORDER_STATUS_PICKUP_WAIT = 9
ORDER_STATUS_PICKUP_COMPLETED = 10

ORDER_STATUS = [
    (ORDER_STATUS_PAYMENT_WAIT, '결제 대기'),
    (ORDER_STATUS_PAYMENT_COMPLETED, '결제 성공'),
    (ORDER_STATUS_REFUND_WAIT, '환불 대기'),
    (ORDER_STATUS_REFUND_COMPLETED, '환불 성공'),
    (ORDER_STATUS_ORDER_CONFIRM_WAIT, '주문 확인중'),
    (ORDER_STATUS_ORDER_CONFIRMED, '주문 완료'),
    (ORDER_STATUS_ORDER_EXPIRED, '주문 만료'),
    (ORDER_STATUS_ORDER_CONFIRMED, '주문 취소'),
    (ORDER_STATUS_PICKUP_PREPARE,  '픽업 준비중'),
    (ORDER_STATUS_PICKUP_WAIT,  '픽업 대기중'),
    (ORDER_STATUS_PICKUP_COMPLETED, '픽업 완료'),
]

# ORDER RECORD
ORDER_RECORD_GET_MENU = 0
ORDER_RECORD_SET_PICKUP_TIEM = 1
ORDER_RECORD_ORDERSHEET_CHECK = 2
ORDER_RECORD_PAYMENT = 3
ORDER_RECORD_PAYMENT_COMPLETED = 4

ORDER_RECORD = [
    (ORDER_RECORD_GET_MENU, '메뉴보기'),
    (ORDER_RECORD_SET_PICKUP_TIEM, '픽업시간 설정'),
    (ORDER_RECORD_ORDERSHEET_CHECK, '주문 확인'),
    (ORDER_RECORD_PAYMENT, '결제준비'),
    (ORDER_RECORD_PAYMENT_COMPLETED, '결제완료'),
]

# PICKUP TIME
LUNCH_PICKUP_TIME = [
    (0, "11:30"), (1, "11:45"), (2, "12:00"), (3, "12:15"), 
    (4, "12:30"), (5, "12:45"), (6, "13:00"), (7, "13:15"), (8, "13:30")
]

DINNER_PICKUP_TIME = [
    (0, "17:30"), (1, "18:00"), (2, "18:30"),
    (3, "19:00"), (4, "19:30"), (5, "20:00"), (6, "20:30"), (7, "21:00")
]

# OPEN & CLOSE

OC_OPEN = 0
OC_CLOSE = 1
OC_STATUS = [
    (OC_OPEN, 'Open'),
    (OC_CLOSE, 'Close'),
]

# Kakao Param Data
KAKAO_BLOCK_SIGNUP = '5ddf9007ffa7480001986cdc'
KAKAO_BLOCK_HOME = '5d3fd7ceffa7480001a73c68'
KAKAO_BLOCK_GET_MENU = '5d5f9009b617ea0001c13f4b'
KAKAO_BLOCK_SET_PICKUP_TIME = '5de12635b617ea0001cb037a'
KAKAO_BLOCK_SET_ORDER_SHEET = '5d6cd9f1ffa7480001c1edf7'


KAKAO_BLOCK_EDIT_PICKUP_TIME = '5d70c71392690d000181340e'
KAKAO_BLOCK_EDIT_PICKUP_TIME_CONFIRM = '5d846d3e92690d000146432f'

KAKAO_BLOCK_EATPLE_PASS = '5d6f6609ffa7480001c1fdb3'
KAKAO_BLOCK_RECENT_ORDER = '5d706aed92690d0001812e49'

KAKAO_PARAM_ORDER_ID = 'order_id'
KAKAO_PARAM_STORE_ID = 'store_id'
KAKAO_PARAM_MENU_ID = 'menu_id'

KAKAO_PARAM_MENU_CATEGORY = 'menuCategory'
KAKAO_PARAM_PICKUP_TIME = 'pickup_time'


# Time Functions
def dateNowByTimeZone():
    """
    Returns an aware or naive datetime.datetime, depending on settings.USE_TZ.
    """
    if settings.USE_TZ:
        tz = pytz.timezone(settings.TIME_ZONE)
        return tz.localize(datetime.now())
    else:
        return datetime.now()


def dateByTimeZone(datetime):
    try:
        tz = pytz.timezone(settings.TIME_ZONE)
        return tz.localize(datetime)
    except ValueError as ex:
        timeDiffrence = timedelta(hours=9)
        KST = timezone(timeDiffrence)

        localeTime = datetime.replace(tzinfo=KST) + timeDiffrence
        
        return localeTime # TO Korea
