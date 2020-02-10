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
        DEBUG_DAYS = 6
        DEBUG_HOUR = 16
        DEBUG_MIN = 30
        DEBUG_SEC = 00

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
