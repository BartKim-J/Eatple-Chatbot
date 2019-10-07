'''
    Author : Ben Kim

    @NOTE
    @BUG
    @TODO
 
'''
#Django Library
from django.conf import settings

#External Library
from datetime import datetime, timedelta, timezone
import pytz

#SYSTEM LOCAL DEFINE
STRING_32BIT  = 31
STRING_256BIT = 255


EATPLUS_HOST_URL = "http://54.65.75.156:8000"
VALUE_NOT_APPLICABLE = 'N/A'

#Eatplus App Global Defines
class EP_define():
    #SYSTEM
    USE_TZ               = settings.USE_TZ
    TIME_ZONE            = settings.TIME_ZONE
    
    HOST_URL             = EATPLUS_HOST_URL

    NOT_APPLICABLE       = VALUE_NOT_APPLICABLE
    DEFAULT_OBJECT_ID    = 1
    DEFAULT_USER_ID      = 2

    #IMAGE DB PATH
    PATH_IMG_DB                 = "STORE_DB/images"

    
    #USER LENGTH
    USER_NICKNAME_LENGTH = STRING_32BIT
    USER_ID_LENGTH       = STRING_32BIT
    USER_ID_CODE_LENGTH  = STRING_256BIT

    #PARTNER LENGTH
    PARTNER_ID_CODE_LENGTH  = STRING_256BIT

    #STRING LENGTH
    STRING_LENGTH        = STRING_256BIT
    WORD_LENGTH          = STRING_32BIT

    #MENU
    MANAGEMENT_CODE_DEFAULT    = VALUE_NOT_APPLICABLE
    MANAGEMENT_CODE_LENGTH     = STRING_256BIT

    SELLING_TIME_LUNCH         = 0
    SELLING_TIME_DINNER        = 1
    SELLING_TIME_CATEGORY_DICT = {'점심': SELLING_TIME_LUNCH, '저녁': SELLING_TIME_DINNER}
    SELLING_TIME_CATEGORY      = [('점심', '점심'), ('저녁', '저녁'),]

    #ORDERING
    ORDER_STATUS_DICT = {'주문 확인중': 0, '주문 완료': 1, '픽업 준비중': 2, '픽업 가능': 3, '픽업 완료': 4, '주문 만료': 5, '주문 취소': 6}
    ORDER_STATUS = [
        ('주문 확인중',  '주문 확인중'), ('주문 완료',   '주문 완료'), ('픽업 준비중',  '픽업 준비중'),
        ('픽업 가능',   '픽업 가능'), ('픽업 완료',   '픽업 완료'),
        ('주문 만료',   '주문 만료'), ('주문 취소',   '주문 취소'),]

    #PICKUP TIME
    LUNCH_PICKUP_TIME  = [ (0, "11:30"), (1, "11:45"), (2, "12:00"), (3, "12:15"), (4, "12:30"), (5, "12:45"), (6, "13:00"), (7, "13:15"), (8, "13:30") ]
    DINNER_PICKUP_TIME = [ (0, "17:30"), (1, "18:00"), (2, "18:30"), (3, "19:00"), (4, "19:30"), (5, "20:00"), (6, "20:30"), (7, "21:00") ]

    #Kakao Param Data
    KAKAO_PARAM_ORDER_ID          = 'orderID'
    KAKAO_PARAM_STORE_ID          = 'storeID'
    KAKAO_PARAM_MENU_ID           = 'menuID' 

    KAKAO_PARAM_MENU_CATEGORY     = 'menuCategory'
    KAKAO_PARAM_SELLING_TIME      = 'sellingTime'
    KAKAO_PARAM_PICKUP_TIME       = 'pickupTime'

    KAKAO_PARAM_STATUS            = 'status'
    KAKAO_PARAM_STATUS_OK         = True
    KAKAO_PARAM_STATUS_NOT_OK     = False


#Time Functions
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
        KST = timezone(timedelta(hours=9))
        return datetime.replace(tzinfo=KST) # TO Korea