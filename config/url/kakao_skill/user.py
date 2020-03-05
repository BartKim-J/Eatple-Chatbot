from django.urls import path, include
from django.conf.urls import url

from eatple_app import views

# Urls - User App
KAKAO_SKILL_USER_URLS = [
    # Test
    #path('skill/user/test', views.GET_Test),

    # Home
    path('skill/user/home', views.GET_UserHome),

    # Order Flow
    path('skill/user/order/get_menu',         views.GET_Menu),
    path('skill/user/order/set_pickup_time',   views.SET_PickupTime),
    path('skill/user/order/set_order_sheet',   views.SET_OrderSheet),

    # Order View Flow
    path('skill/user/orderView/get_order_details', views.GET_OrderDetails),
    path('skill/user/orderView/get_eatple_pass',    views.GET_EatplePass),

    # Order Edit Flow
    path('skill/user/orderEdit/post_order_cancel',     views.POST_OrderCancel),

    path('skill/user/orderEdit/get_confirm_use_eatplepass',
         views.GET_ConfirmUseEatplePass),
    path('skill/user/orderEdit/post_use_eatplepass',
         views.POST_UseEatplePass),

    # Order Pickup Time Change Flow
    path('skill/user/orderEdit/get_edit_pickup_time',
         views.GET_EditPickupTime),
    path('skill/user/orderEdit/set_confirm_edit_pickup_time',
         views.SET_ConfirmEditPickupTime),

    # Order Share
    path('skill/user/orderShare/get_delegate_user_remove',
         views.GET_DelegateUserRemove),
    path('skill/user/orderShare/get_delegate_user_remove_all',
         views.GET_DelegateUserRemoveAll),
    path('skill/user/orderShare/get_delegate_user',
         views.GET_DelegateUser),

    # Notify
    path('skill/user/etc/get_notify', views.GET_UserNotify),
]

KAKAO_SKILL_USER_EVENT_URLS = [
    # Home
    path('skill/promotion/home', views.GET_ProMotionHome),
]
