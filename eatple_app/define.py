# System
import sys
import os

# Django Library
from django.conf import settings
from django.utils import timezone

# External Library
import datetime

import requests
import json

import pytz

from iamport import Iamport


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
ORDER_STATUS_PAYMENT_CHECK = 0
ORDER_STATUS_ORDER_CONFIRM_WAIT = 1
ORDER_STATUS_ORDER_CONFIRMED = 2
ORDER_STATUS_ORDER_EXPIRED = 3
ORDER_STATUS_ORDER_CANCELED = 4
ORDER_STATUS_PICKUP_PREPARE = 5
ORDER_STATUS_PICKUP_WAIT = 6
ORDER_STATUS_PICKUP_COMPLETED = 7
ORDER_STATUS_ORDER_FAILED = 100

ORDER_STATUS = [
    (ORDER_STATUS_PAYMENT_CHECK, '결제 확인중'),
    (ORDER_STATUS_ORDER_CONFIRM_WAIT, '주문 대기중'),
    (ORDER_STATUS_ORDER_CONFIRMED, '주문 완료'),
    (ORDER_STATUS_ORDER_EXPIRED, '주문 만료'),
    (ORDER_STATUS_ORDER_CANCELED, '주문 취소'),
    (ORDER_STATUS_PICKUP_PREPARE,  '픽업 준비중'),
    (ORDER_STATUS_PICKUP_WAIT,  '픽업 대기중'),
    (ORDER_STATUS_PICKUP_COMPLETED, '픽업 완료'),
    
    
    (ORDER_STATUS_ORDER_FAILED, '주문실패')
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
    (ORDER_RECORD_PAYMENT, '결제확인'),
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


# IamPort
IAMPORT_API_KEY = '8060686596108918'
IAMPORT_API_SECRET_KEY = 'Ag2i32vX2b0H4Cc4hl76jdZI8fYaMqOnHRGKTbIWnIDslPwDbDJvQJdZZcaMCY9kPP5I1NEpvhRQ7nui'

IAMPORT_ORDER_STATUS_PAID = 'paid'
IAMPORT_ORDER_STATUS_CANCLED = 'cancelled'
IAMPORT_ORDER_STATUS_FAILED = 'failed'
IAMPORT_ORDER_STATUS_READY = 'ready'

IAMPORT_ORDER_STATUS = [
    (IAMPORT_ORDER_STATUS_READY, '미결제'),
    (IAMPORT_ORDER_STATUS_PAID, '결제완료'),
    (IAMPORT_ORDER_STATUS_CANCLED, '환불/취소'),
    (IAMPORT_ORDER_STATUS_FAILED, '결제실패'),
]

# Kakao API KEY
KAKAO_API_KEY = "d62991888c78ec58d809bdc591eb62f6"
KAKAO_REST_API_KEY = "9120ecde0549629d5a049e9755541e5e"

# Kakao Param Data
KAKAO_BLOCK_SIGNUP = '5ddf9007ffa7480001986cdc'
KAKAO_BLOCK_HOME = '5d3fd7ceffa7480001a73c68'
KAKAO_BLOCK_GET_MENU = '5d5f9009b617ea0001c13f4b'
KAKAO_BLOCK_SET_PICKUP_TIME = '5de12635b617ea0001cb037a'
KAKAO_BLOCK_SET_ORDER_SHEET = '5d6cd9f1ffa7480001c1edf7'

KAKAO_BLOCK_POST_ORDER_CANCEL ='5d70befab617ea0001c193bd'

KAKAO_BLOCK_EDIT_PICKUP_TIME = '5d70c71392690d000181340e'
KAKAO_BLOCK_EDIT_PICKUP_TIME_CONFIRM = '5d846d3e92690d000146432f'

KAKAO_BLOCK_EATPLE_PASS = '5d6f6609ffa7480001c1fdb3'
KAKAO_BLOCK_ORDER_DETAILS = '5d706aed92690d0001812e49'

KAKAO_PARAM_ORDER_ID = 'order_id'
KAKAO_PARAM_STORE_ID = 'store_id'
KAKAO_PARAM_MENU_ID = 'menu_id'
KAKAO_PARAM_PREV_BLOCK_ID = 'prev_block_id'

KAKAO_PARAM_MENU_CATEGORY = 'menuCategory'
KAKAO_PARAM_PICKUP_TIME = 'pickup_time'


# Time Functions
def dateNowByTimeZone():
    """
    Returns an aware or naive datetime, depending on settings.USE_TZ.
    """
    if settings.USE_TZ:
        tz = pytz.timezone(settings.TIME_ZONE)
        return tz.localize(datetime.datetime.now())
    else:
        return datetime.datetime.now()


def dateByTimeZone(UTC):
    try:
        tz = pytz.timezone(settings.TIME_ZONE)
        return tz.localize(UTC)
    except ValueError as ex:
        timeDiffrence = datetime.timedelta(hours=9)
        KST = datetime.timezone(timeDiffrence)

        localeTime = UTC.replace(tzinfo=KST) + timeDiffrence
        
        return localeTime # TO Korea
