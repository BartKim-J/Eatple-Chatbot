# System
import os
import sys
from random import *

# Django Library
from django.conf import settings
from django.utils import timezone

# External Library
import datetime

import requests
import json

import pytz

from eatple_app.module_iamport.Iamport import Iamport
from eatple_app.views_slack.slack_logger import *

from phonenumber_field.modelfields import PhoneNumberField

from django_admin_listfilter_dropdown.filters import DropdownFilter, RelatedDropdownFilter, ChoiceDropdownFilter

from rangefilter.filter import DateRangeFilter, DateTimeRangeFilter

from import_export.admin import ExportActionModelAdmin, ImportExportMixin, ImportMixin
from import_export.fields import Field
from import_export import resources

from mapwidgets.widgets import GooglePointFieldWidget, GoogleStaticMapWidget

from django.contrib.gis.geos import *
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance

from django.db.models import F

VALUE_NOT_APPLICABLE = 'N/A'

# Eatplus App Global Defines
STRING_32 = 31
STRING_256 = 255

USE_TZ = settings.USE_TZ
TIME_ZONE = settings.TIME_ZONE

HOST_URL = 'https://www.eatple.com:8000'

NOT_APPLICABLE = VALUE_NOT_APPLICABLE

# IMAGE DB PATH
PATH_IMG_DB = 'STORE_DB/images'

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

SELLING_TIME_LUNCH = 'lunch'
SELLING_TIME_DINNER = 'dinner'
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
ORDER_STATUS_MENU_CHOCIED = 101

ORDER_STATUS = [
    (ORDER_STATUS_PAYMENT_CHECK, '결제 확인중'),
    (ORDER_STATUS_ORDER_CONFIRM_WAIT, '주문 대기중'),
    (ORDER_STATUS_ORDER_CONFIRMED, '주문 완료'),
    (ORDER_STATUS_ORDER_EXPIRED, '주문 만료'),
    (ORDER_STATUS_ORDER_CANCELED, '주문 취소'),
    (ORDER_STATUS_PICKUP_PREPARE,  '픽업 준비중'),
    (ORDER_STATUS_PICKUP_WAIT,  '픽업 대기중'),
    (ORDER_STATUS_PICKUP_COMPLETED, '픽업 완료'),


    (ORDER_STATUS_ORDER_FAILED, '주문실패'),
    (ORDER_STATUS_MENU_CHOCIED, '메뉴 선택'),
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
    (0, '11:30'), (1, '11:45'), (2, '12:00'), (3, '12:15'),
    (4, '12:30'), (5, '12:45'), (6, '13:00'), (7, '13:15'), (8, '13:30')
]

DINNER_PICKUP_TIME = [
    (0, '17:30'), (1, '18:00'), (2, '18:30'),
    (3, '19:00'), (4, '19:30'), (5, '20:00'), (6, '20:30'), (7, '21:00')
]

# OPEN & CLOSE
OC_OPEN = 'open'
OC_CLOSE = 'close'
OC_STATUS = [
    (OC_OPEN, '열림'),
    (OC_CLOSE, '닫힘'),
]

#  TYPE
ORDER_TYPE_NORMAL = 'normal'
ORDER_TYPE_EVENT = 'event'
ORDER_TYPE_PROMOTION = 'promotion'
ORDER_TYPE_B2B = 'B2B'
ORDER_TYPE = [
    (ORDER_TYPE_NORMAL, '일반'),
    (ORDER_TYPE_EVENT, '이벤트'),
    (ORDER_TYPE_PROMOTION, '프로모션'),
    (ORDER_TYPE_B2B, 'B2B'),
]


# STORE_TYPE
STORE_TYPE_NORMAL = 'normal'
STORE_TYPE_B2B = 'B2B'
STORE_TYPE_EVENT = 'event'
STORE_TYPE_PROMOTION = 'promotion'
STORE_TYPE = [
    (STORE_TYPE_NORMAL, '일반'),
    (STORE_TYPE_EVENT, '이벤트'),
    (STORE_TYPE_B2B, 'B2B'),
]

# USER_TYPE
USER_TYPE_NORMAL = 'normal'
USER_TYPE_B2B = 'b2b'
USER_TYPE_ADMIN = 'admin'
USER_TYPE = [
    (USER_TYPE_NORMAL, '일반'),
    (USER_TYPE_B2B, 'B2B'),
    (USER_TYPE_ADMIN, '관리자'),
]

# PARTNER_TYPE
PARTNER_TYPE_NORMAL = 'normal'
PARTNER_TYPE_ADMIN = 'admin'
PARTNER_TYPE = [
    (PARTNER_TYPE_NORMAL, '일반'),
    (PARTNER_TYPE_ADMIN, '점주'),
]

# AREA_CODE
STORE_AREA_A_1 = 'A1'
STORE_AREA_A_2 = 'A2'
STORE_AREA_A_3 = 'A3'
STORE_AREA_A_4 = 'A4'

STORE_AREA_B_1 = 'B1'
STORE_AREA_B_2 = 'B2'

STORE_AREA_C_1 = 'C1'
STORE_AREA_C_2 = 'C2'
STORE_AREA_C_3 = 'C3'
STORE_AREA_C_4 = 'C4'

STORE_AREA_Z_1 = 'Z1'

STORE_AREA = [
    (STORE_AREA_A_1, '강남 1호점'),
    (STORE_AREA_A_2, '강남 2호점'),
    (STORE_AREA_A_3, '강남 3호점'),
    (STORE_AREA_A_4, '강남 4호점'),

    (STORE_AREA_B_1, '역삼 1호점'),
    (STORE_AREA_B_2, '역삼 2호점'),

    (STORE_AREA_C_1, '강남역'),
    (STORE_AREA_C_2, '역삼역'),
    (STORE_AREA_C_3, '삼성역'),
    (STORE_AREA_C_4, '선릉역'),

    (STORE_AREA_Z_1, '기타 지역'),
]


# IAMPORT
IAMPORT_API_KEY = '8060686596108918'
IAMPORT_API_SECRET_KEY = 'Ag2i32vX2b0H4Cc4hl76jdZI8fYaMqOnHRGKTbIWnIDslPwDbDJvQJdZZcaMCY9kPP5I1NEpvhRQ7nui'

IAMPORT_ORDER_STATUS_PAID = 'paid'
IAMPORT_ORDER_STATUS_CANCELLED = 'cancelled'
IAMPORT_ORDER_STATUS_FAILED = 'failed'
IAMPORT_ORDER_STATUS_READY = 'ready'

IAMPORT_ORDER_STATUS_NOT_PUSHED = 'not_pushed'

IAMPORT_ORDER_STATUS = [
    (IAMPORT_ORDER_STATUS_READY, '미결제'),
    (IAMPORT_ORDER_STATUS_PAID, '결제완료'),
    (IAMPORT_ORDER_STATUS_CANCELLED, '환불/취소'),
    (IAMPORT_ORDER_STATUS_FAILED, '결제실패'),

    (IAMPORT_ORDER_STATUS_NOT_PUSHED, '메뉴 선택중'),
]

# Kakao API KEY
KAKAO_API_KEY = 'd62991888c78ec58d809bdc591eb62f6'
KAKAO_REST_API_KEY = '9120ecde0549629d5a049e9755541e5e'

# Kakao Block ID
# User
KAKAO_BLOCK_USER_SIGNUP = '5de6ec7effa74800014ac035'
KAKAO_BLOCK_USER_HOME = '5de6ea80b617ea000159b042'

KAKAO_BLOCK_USER_GET_MENU = '5de6ebc092690d0001fbc16f'
KAKAO_BLOCK_USER_SET_PICKUP_TIME = '5de6ebd092690d0001fbc173'
KAKAO_BLOCK_USER_SET_ORDER_SHEET = '5de6ebc892690d0001fbc171'

KAKAO_BLOCK_USER_POST_ORDER_CANCEL = '5de6ebdb92690d0001fbc175'

KAKAO_BLOCK_USER_POST_USE_EATPLE_PASS = '5de6ec2f92690d0001fbc183'
KAKAO_BLOCK_USER_GET_USE_EATPLE_PASS_CONFIRM = '5de6ec2892690d0001fbc181'

KAKAO_BLOCK_USER_EDIT_PICKUP_TIME = '5de6ebe692690d0001fbc177'
KAKAO_BLOCK_USER_EDIT_PICKUP_TIME_CONFIRM = '5de6ebf292690d0001fbc179'

KAKAO_BLOCK_USER_EATPLE_PASS = '5de6ec1b92690d0001fbc17d'
KAKAO_BLOCK_USER_ORDER_DETAILS = '5de6ec2192690d0001fbc17f'

KAKAO_BLOCK_USER_INTRO = '5de6ecc88192ac0001780f1f'
KAKAO_BLOCK_USER_MANUAL = '5de6ed01b617ea000159b04d'

KAKAO_BLOCK_USER_EDIT_LOCATION = '5de6ecf98192ac0001780f21'

KAKAO_BLOCK_USER_PROMOTION = '5de6eb4692690d0001fbc16b'

# Partner
KAKAO_BLOCK_PARTNER_SIGNUP = '5de414378192ac0001d65d41'
KAKAO_BLOCK_PARTNER_STORE_REGISTRATION = '5de4148892690d0001983f67'
KAKAO_BLOCK_PARTNER_HOME = '5dd23dfdffa748000155115a'
KAKAO_BLOCK_PARTNER_GET_ORDER_DETAILS = '5dd23e8a8192ac000119ec0b'
KAKAO_BLOCK_PARTNER_CALCULATE = '5de63a0effa74800014abe15'

KAKAO_BLOCK_PARTNER_INTRO = '5de419a18192ac0001d65d49'
KAKAO_BLOCK_PARTNER_MANUAL = '5dd24577ffa74800015511fa'

KAKAO_BLOCK_USER_ORDER_SHARING_START = '5e1ea6458192ac0001a1844e'
KAKAO_BLOCK_USER_ORDER_SHARING_CANCEL = '5e2566eab617ea0001302716'
KAKAO_BLOCK_USER_ORDER_SHARING_CANCEL_ALL = '5e26804e92690d0001fc4c76'

# Kakao Param ID
KAKAO_PARAM_ORDER_ID = 'order_id'
KAKAO_PARAM_STORE_ID = 'store_id'
KAKAO_PARAM_MENU_ID = 'menu_id'
KAKAO_PARAM_PREV_BLOCK_ID = 'prev_block_id'

KAKAO_PARAM_MENU_CATEGORY = 'menuCategory'
KAKAO_PARAM_PICKUP_TIME = 'pickup_time'


# Location

LOCATION_DEFAULT_ADDR = '강남 사거리'
LOCATION_DEFAULT_LAT = 37.497907
LOCATION_DEFAULT_LNG = 127.027635


# DEBUG MODE FLAG
ORDERING_DEBUG_MODE = False
ORDER_TIME_CHECK_DEBUG_MODE = True
VALIDATION_DEBUG_MODE = False

# Time Functions
def dateNowByTimeZone():
    '''
    Returns an aware or naive datetime, depending on settings.USE_TZ.
    '''
    # Time QA DEBUG
    if(ORDER_TIME_CHECK_DEBUG_MODE):
        DEBUG_DAYS = 23
        DEBUG_HOUR = 9
        DEBUG_MIN = 55

        if settings.USE_TZ:
            tz = pytz.timezone(settings.TIME_ZONE)
            return tz.localize(datetime.datetime.now()).replace(day=DEBUG_DAYS, hour=DEBUG_HOUR, minute=DEBUG_MIN, second=0, microsecond=0)
        else:
            return datetime.datetime.now().replace(day=DEBUG_DAYS, hour=DEBUG_HOUR, minute=DEBUG_MIN, second=0, microsecond=0)
    else:
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

        return localeTime  # TO Korea
