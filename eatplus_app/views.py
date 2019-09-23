'''
    Author : Ben Kim

    @NOTE
    @BUG
    @TODO
 
'''
### API Functions ###
'''
    Eatplus API for User

    @NOTE
    @BUG
    @TODO

'''
from eatplus_app.views_user.home import userHome
from eatplus_app.views_user.manual import userManual
from eatplus_app.views_user.ordering import getSellingTime, selectMenu, getPickupTime, orderConfirm, orderPush
from eatplus_app.views_user.orderCheck import getOrderList, getCoupon, confirmUseCoupon
from eatplus_app.views_user.orderChange import useCoupon, orderCancel, orderPickupTimeChange, getOrderPickupTime

'''
    Eatplus API for Partner

    @NOTE
    @BUG
    @TODO
    
'''
from eatplus_app.views_partner.home import partnerHome
