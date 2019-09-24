'''
    Author : Ben Kim
    
'''
### API Functions ###
'''
    Eatplus API for User

    @NOTE
    @BUG
    @TODO

'''
#View Main
from eatplus_app.views_user.home       import GET_UserHome

#View Ordering
from eatplus_app.views_user.ordering   import GET_SellingTime
from eatplus_app.views_user.ordering   import GET_Menu
from eatplus_app.views_user.ordering   import GET_PickupTime
from eatplus_app.views_user.ordering   import SET_OrderSheet
from eatplus_app.views_user.ordering   import POST_Order

#View OrderEdit
from eatplus_app.views_user.orderEdit  import GET_ConfirmUserCoupon
from eatplus_app.views_user.orderEdit  import POST_UseCoupon
from eatplus_app.views_user.orderEdit  import POST_OrderCancel
from eatplus_app.views_user.orderEdit  import GET_PickupTimeForChange
from eatplus_app.views_user.orderEdit  import SET_PickupTimeByChanged

#View OrderCheck
from eatplus_app.views_user.orderCheck import GET_OrderList
from eatplus_app.views_user.orderCheck import GET_Coupon

#View ETC
from eatplus_app.views_user.etc     import GET_UserManual
from eatplus_app.views_user.etc     import GET_UserIntro

'''
    Eatplus API for Partner

    @NOTE
    @BUG
    @TODO
    
'''
from eatplus_app.views_partner.home import GET_PartnerHome


#View OrderCheck
from eatplus_app.views_partner.orderCheck import GET_StoreOrderList
from eatplus_app.views_partner.calculateCheck import GET_CalculateCheck

#View ETC
from eatplus_app.views_partner.etc import GET_PartnerManual
from eatplus_app.views_partner.etc import GET_PartnerIntro