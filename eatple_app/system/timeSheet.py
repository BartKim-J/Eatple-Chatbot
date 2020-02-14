# External Library
import datetime
import pytz

###########################################################################################
# System
from eatple_app.system.mode import *

# Django Library
from django.conf import settings
from django.utils import timezone

USE_TZ = settings.USE_TZ
TIME_ZONE = settings.TIME_ZONE

# Time Functions


def dateNowByTimeZone():
    '''
    Returns an aware or naive datetime, depending on settings.USE_TZ.
    '''
    # Time QA DEBUG
    if(ORDER_TIME_CHECK_DEBUG_MODE):
        DEBUG_DAYS = 12
        DEBUG_HOUR = 18
        DEBUG_MIN = 55
        DEBUG_SEC = 0

        if settings.USE_TZ:
            tz = pytz.timezone(settings.TIME_ZONE)
            return tz.localize(datetime.datetime.now()).replace(day=DEBUG_DAYS, hour=DEBUG_HOUR, minute=DEBUG_MIN, second=DEBUG_SEC)
        else:
            return datetime.datetime.now().replace(day=DEBUG_DAYS, hour=DEBUG_HOUR, minute=DEBUG_MIN, second=DEBUG_SEC)
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


def dateByUTC(KOR):
    timeDiffrence = datetime.timedelta(hours=-9)
    UTC = datetime.timezone(datetime.timedelta(hours=0))

    localeTime = KOR.replace(tzinfo=UTC) + timeDiffrence

    return localeTime  # TO Korea


class OrderTimeSheet():
    def __init__(self):
        self.currentDate = dateNowByTimeZone().replace(microsecond=0)
        self.currentDateWithoutTime = self.currentDate.replace(
            hour=0, minute=0, second=0)

        self.yesterday = self.currentDateWithoutTime + \
            datetime.timedelta(days=-1)  # Yesterday start
        self.today = self.currentDateWithoutTime
        self.tomorrow = self.currentDateWithoutTime + \
            datetime.timedelta(days=1)  # Tommorrow start

    def GetCurrentDate(self):
        return self.currentDate

    def GetCurrentDateWithoutTime(self):
        return self.currentDateWithoutTime

    def GetToday(self):
        return self.today

    def GetYesterDay(self):
        return self.yesterday

    def GetTomorrow(self):
        return self.tomorrow

    # Prev Lunch Order Edit Time
    def GetPrevLunchOrderEditTimeStart(self):
        return self.currentDateWithoutTime + \
            datetime.timedelta(hours=16, minutes=30, days=-1)

    def GetPrevLunchOrderEditTimeEnd(self):
        return self.currentDateWithoutTime + \
            datetime.timedelta(hours=10, minutes=30)

    def GetPrevLunchOrderTimeEnd(self):
        return self.currentDateWithoutTime + \
            datetime.timedelta(hours=10, minutes=30)

    # Dinner Order Edit Time
    def GetDinnerOrderEditTimeStart(self):
        return self.currentDateWithoutTime + \
            datetime.timedelta(hours=11, minutes=30)

    def GetDinnerOrderEditTimeEnd(self):
        return self.currentDateWithoutTime + \
            datetime.timedelta(hours=16, minutes=30)

    def GetDinnerOrderTimeEnd(self):
        return self.currentDateWithoutTime + \
            datetime.timedelta(hours=16, minutes=30)

    # Next Lunch Order Edit Time
    def GetNextLunchOrderEditTimeStart(self):
        return self.currentDateWithoutTime + \
            datetime.timedelta(hours=16, minutes=30)

    def GetNextLunchOrderEditTimeEnd(self):
        return self.currentDateWithoutTime + \
            datetime.timedelta(hours=9, minutes=30, days=1)

    def GetNextLunchOrderTimeEnd(self):
        return self.currentDateWithoutTime + \
            datetime.timedelta(hours=10, minutes=30, days=1)

    # Lunch Order Pickup Time
    def GetLunchOrderPickupTimeStart(self):
        return self.currentDateWithoutTime + \
            datetime.timedelta(hours=11, minutes=30)

    def GetLunchOrderPickupTimeEnd(self):
        return self.currentDateWithoutTime + \
            datetime.timedelta(hours=16, minutes=0)

    # Dinner Order Pickup Time
    def GetDinnerOrderPickupTimeStart(self):
        return self.currentDateWithoutTime + \
            datetime.timedelta(hours=17, minutes=30)

    def GetDinnerOrderPickupTimeEnd(self):
        return self.currentDateWithoutTime + \
            datetime.timedelta(hours=21, minutes=0)

    # Backend Counter Time
    def GetInitialCountTime(self):
        return self.currentDateWithoutTime + \
            datetime.timedelta(hours=16, minutes=0)

    def GetOrderExpireDate(self):
        return self.currentDate + datetime.timedelta(hours=-24)