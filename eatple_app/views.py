# User
# Home
from eatple_app.views_user.home import GET_UserHome

# Ordeirng
from eatple_app.views_user.ordering import GET_Menu
from eatple_app.views_user.ordering import SET_PickupTime
from eatple_app.views_user.ordering import SET_OrderSheet

# Edit
from eatple_app.views_user.orderCheck import GET_EatplePass
from eatple_app.views_user.orderCheck import GET_OrderDetails

from eatple_app.views_user.orderEdit import GET_ConfirmUserCoupon
from eatple_app.views_user.orderEdit import POST_UseCoupon
from eatple_app.views_user.orderEdit import POST_OrderCancel
from eatple_app.views_user.orderEdit import GET_PickupTimeForChange
from eatple_app.views_user.orderEdit import SET_PickupTimeByChanged



from eatple_app.views_user.etc import GET_UserManual
from eatple_app.views_user.etc import GET_UserIntro

# Partner
from eatple_app.views_partner.home import GET_PartnerHome
from eatple_app.views_partner.orderCheck import GET_StoreOrderList
from eatple_app.views_partner.calculateCheck import GET_CalculateCheck
from eatple_app.views_partner.etc import GET_PartnerManual
from eatple_app.views_partner.etc import GET_PartnerIntro
from eatple_app.views_partner.alarm import GET_OpenLunchStoreAlarm
from eatple_app.views_partner.alarm import GET_CloseLunchStoreAlarm
from eatple_app.views_partner.alarm import GET_OpenDinnerStoreAlarm
from eatple_app.views_partner.alarm import GET_CloseDinnerStoreAlarm
from eatple_app.views_partner.alarm import GET_PickupAlarm
from eatple_app.views_partner.alarm import GET_PickupBlockEnableAlarm
from eatple_app.views_partner.alarm import GET_PickupBlockDisableAlarm
