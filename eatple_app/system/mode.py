# Django Library
from django.conf import settings

###########################################################################################
# DEBUG MODE FLAG
DEBUG_USER_ID = 1319148379

if(settings.SETTING_ID == 'DEPLOY'):
    ORDER_TIME_CHECK_DEBUG_MODE = False
    VALIDATION_DEBUG_MODE = False
    USER_ID_DEBUG_MODE = False
    PAYMENT_TIME_CHECK_DEBUG_MODE = True

elif(settings.SETTING_ID == 'DEBUG'):
    ORDER_TIME_CHECK_DEBUG_MODE = True
    VALIDATION_DEBUG_MODE = False
    USER_ID_DEBUG_MODE = False
    PAYMENT_TIME_CHECK_DEBUG_MODE = False

else:
    ORDER_TIME_CHECK_DEBUG_MODE = False
    VALIDATION_DEBUG_MODE = False
    USER_ID_DEBUG_MODE = False
    PAYMENT_TIME_CHECK_DEBUG_MODE = False
