# Django Library
from django.conf import settings

if(settings.SETTING_ID == 'DEPLOY'):
    HOST_URL = 'https://eapi.eatple.com'
else:
    HOST_URL = 'https://dev.eatple.com'

# DEFAULT IMAEG URL
# IMAGE DB PATH
PATH_IMG_DB = 'STORE_DB/images'

PARTNER_ORDER_SHEET_IMG = '/media/STORE_DB/images/default/partnerOrderSheet.png'

EATPLE_HOME_LUNCH_IMG = '/media/STORE_DB/images/default/homeLunch_03.png'
EATPLE_HOME_DINNER_IMG = '/media/STORE_DB/images/default/homeDinner_04.png'

EATPLE_HEADER_LUNCH_IMG = '/media/STORE_DB/images/default/headerLunch_03.png'
EATPLE_HEADER_DINNER_IMG = '/media/STORE_DB/images/default/headerDinner_03.png'

EATPLE_HEADER_LUNCH_EVENT_IMG = '/media/STORE_DB/images/default/headerLunchDiscount_01.png'
EATPLE_HEADER_DINNER_EVENT_IMG = '/media/STORE_DB/images/default/headerDinnerDiscount_02.png'

EATPLE_SURVEY_IMG = '/media/STORE_DB/images/default/surveyBeta07.png'

EATPLE_FRIEND_INVITATION_IMG = '/media/STORE_DB/images/default/FriendInvitation_02.png'

EATPLE_MENU_PICKUP_ZONE_FF_IMG = '/media/STORE_DB/images/default/PickupZoneStoreFF_05.png'
EATPLE_MENU_PICKUP_ZONE_FF_SUB_IMG = '/media/STORE_DB/images/default/PickupZoneStoreFF_Sub_03.png'

EATPLE_PASS_IMG_01 = '/media/STORE_DB/images/default/EatplePass_01.png'
EATPLE_PASS_IMG_02 = '/media/STORE_DB/images/default/EatplePass_02.png'
EATPLE_PASS_IMG_03 = '/media/STORE_DB/images/default/EatplePass_03.png'
EATPLE_PASS_IMG_04 = '/media/STORE_DB/images/default/EatplePass_04.png'
EATPLE_PASS_IMG_05 = '/media/STORE_DB/images/default/EatplePass_05.png'
EATPLE_PASS_IMG_DINNER = '/media/STORE_DB/images/default/EatplePass_Dinner.png'
EATPLE_PASS_IMG_MORE = '/media/STORE_DB/images/default/EatplePass_More.png'
EATPLE_PASS_IMG_NULL = '/media/STORE_DB/images/default/EatplePass_Null.png'

HOME_HEAD_IMG_URL = '/media/STORE_DB/images/default/homeHead.png'
HOME_HEAD_BLACK_IMG_URL = '/media/STORE_DB/images/default/homeHeadBlack.png'
