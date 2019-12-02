# User
# Home
from eatple_app.views_user.home import GET_UserHome

# Ordeirng
from eatple_app.views_user.ordering import GET_Menu
from eatple_app.views_user.ordering import SET_PickupTime
from eatple_app.views_user.ordering import SET_OrderSheet

# Check
from eatple_app.views_user.orderCheck import GET_EatplePass
from eatple_app.views_user.orderCheck import GET_OrderDetails

# Edit
from eatple_app.views_user.orderEdit import GET_ConfirmUseEatplePass
from eatple_app.views_user.orderEdit import POST_UseEatplePass

# Order Cancel
from eatple_app.views_user.orderEdit import POST_OrderCancel

# Edit Pickup Time
from eatple_app.views_user.orderEdit import GET_EditPickupTime
from eatple_app.views_user.orderEdit import SET_ConfirmEditPickupTime


# Partner
from eatple_app.views_partner.home import GET_PartnerHome

# Check
from eatple_app.views_partner.orderCheck import GET_ParnterOrderDetails

