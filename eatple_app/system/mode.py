# Django Library
from django.conf import settings

###########################################################################################
# DEBUG MODE FLAG
if(settings.SETTING_ID == 'DEPLOY'):
    ORDERING_DEBUG_MODE = False
    ORDER_TIME_CHECK_DEBUG_MODE = False
    VALIDATION_DEBUG_MODE = False
    USER_ID_DEBUG_MODE = False

elif(settings.SETTING_ID == 'DEBUG'):
    ORDERING_DEBUG_MODE = False
    ORDER_TIME_CHECK_DEBUG_MODE = True
    VALIDATION_DEBUG_MODE = False
    USER_ID_DEBUG_MODE = True

else:
    ORDERING_DEBUG_MODE = False
    ORDER_TIME_CHECK_DEBUG_MODE = False
    VALIDATION_DEBUG_MODE = False
    USER_ID_DEBUG_MODE = False
