"""eatplus URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from django.conf import settings
from django.conf.urls.static import static

from eatple_app import views

# Urls
urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Kakao Plus User Skills
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
    path('skill/user/orderEdit/post_orderCancel',     views.POST_OrderCancel),
    path('skill/user/orderEdit/get_confirmUseCoupon',
         views.GET_ConfirmUserCoupon),
    path('skill/user/orderEdit/post_useCoupon',       views.POST_UseCoupon),

    # Order Pickup Time Change Flow
    path('skill/user/orderEdit/get_pickupTimeForChange',
         views.GET_PickupTimeForChange),
    path('skill/user/orderEdit/set_pickupTimeByChanged',
         views.SET_PickupTimeByChanged),

    # ETC
    path('skill/user/etc/get_userManual', views.GET_UserManual),
    path('skill/user/etc/get_userIntro', views.GET_UserIntro),


    # Kakao Plus Partner Skills
    # Home
    path('skill/partner/home', views.GET_PartnerHome),

    # Order View Flow
    path('skill/partner/orderView/get_orderList', views.GET_StoreOrderList),
    path('skill/partner/orderView/get_calculateCheck', views.GET_CalculateCheck),

    # Order Alram View
    path('skill/partner/alarmView/get_openLunchStore',
         views.GET_OpenLunchStoreAlarm),
    path('skill/partner/alarmView/get_closeLunchStore',
         views.GET_CloseLunchStoreAlarm),
    path('skill/partner/alarmView/get_openDinnerStore',
         views.GET_OpenDinnerStoreAlarm),
    path('skill/partner/alarmView/get_closeDinnerStore',
         views.GET_CloseDinnerStoreAlarm),
    path('skill/partner/alarmView/get_pickup', views.GET_PickupAlarm),
    path('skill/partner/alarmView/get_enablePickupBlock',
         views.GET_PickupBlockEnableAlarm),
    path('skill/partner/alarmView/get_disablePickupBlock',
         views.GET_PickupBlockDisableAlarm),

    # ETC
    path('skill/partner/etc/get_partnerManual', views.GET_PartnerManual),
    path('skill/partner/etc/get_partnerIntro', views.GET_PartnerIntro),
]

# Media Link Url
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
