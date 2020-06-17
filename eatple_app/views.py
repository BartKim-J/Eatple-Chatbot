# User
from eatple_app.views_user.debug import GET_Debug

# Home
from eatple_app.views_user.home import GET_UserHome

# Check
from eatple_app.views_user.orderCheck import GET_EatplePass
from eatple_app.views_user.orderCheck import GET_OrderDetails

# Edit
from eatple_app.views_user.orderEdit import GET_ConfirmUseEatplePass
from eatple_app.views_user.orderEdit import POST_UseEatplePass

# Order Cancel
from eatple_app.views_user.orderEdit import POST_OrderCancel

# Order Share
from eatple_app.views_user.orderShare import GET_DelegateUserRemove
from eatple_app.views_user.orderShare import GET_DelegateUserRemoveAll
from eatple_app.views_user.orderShare import GET_DelegateUser

# Order Edit Pickup Time
from eatple_app.views_user.orderEdit import GET_EditPickupTime
from eatple_app.views_user.orderEdit import SET_ConfirmEditPickupTime

# Order Flow
from eatple_app.views_user.orderFlow import GET_Store
from eatple_app.views_user.orderFlow import GET_Menu
from eatple_app.views_user.orderFlow import SET_PickupTime
from eatple_app.views_user.orderFlow import SET_OrderSheet

# Event
from eatple_app.views_user.delivery_event import POST_DeliveryEnable
from eatple_app.views_user.delivery_event import POST_DeliveryDisable
from eatple_app.views_user.delivery_event import POST_DeliveryAddressSubmit

from eatple_app.views_user.friend_code import GET_FriendInvitation
from eatple_app.views_user.friend_code import POST_FriendCodeSubmit

# Notify
from eatple_app.views_user.notify import GET_UserNotify

# Partner
from eatple_app.views_partner.home import GET_PartnerHome

# Check
from eatple_app.views_partner.orderCheck import GET_ParnterOrderDetails

# Admin

from eatple_app.views_admin.login import POST_AdminLogin
from eatple_app.views_admin.logout import POST_AdminLogout
