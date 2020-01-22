# User
## Home
from eatple_app.views_user.home import GET_UserHome

## Ordeirng
from eatple_app.views_user.ordering import GET_Menu
from eatple_app.views_user.ordering import SET_PickupTime
from eatple_app.views_user.ordering import SET_OrderSheet

## Check
from eatple_app.views_user.orderCheck import GET_EatplePass
from eatple_app.views_user.orderCheck import GET_OrderDetails

## Edit
from eatple_app.views_user.orderEdit import GET_ConfirmUseEatplePass
from eatple_app.views_user.orderEdit import POST_UseEatplePass

## Order Cancel
from eatple_app.views_user.orderEdit import POST_OrderCancel

## Order Share
from eatple_app.views_user.orderShare import GET_DelegateUserRemove
from eatple_app.views_user.orderShare import GET_DelegateUserRemoveAll
from eatple_app.views_user.orderShare import GET_DelegateUser

## Edit Pickup Time
from eatple_app.views_user.orderEdit import GET_EditPickupTime
from eatple_app.views_user.orderEdit import SET_ConfirmEditPickupTime

# User Promotion
## Home
from eatple_app.views_user_promotion.home import GET_ProMotionHome

# Partner
from eatple_app.views_partner.home import GET_PartnerHome

## Check
from eatple_app.views_partner.orderCheck import GET_ParnterOrderDetails

# Kakao 
from eatple_app.views_kakao.channel import POST_KAKAO_ChannelLog

# Slack
from eatple_app.views_slack.slack_api import Events

# Rest Framework
from eatple_app.rest_api.validation import OrderValidation
from eatple_app.rest_api.validation import OrderInformation
