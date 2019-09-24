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

from eatplus_app import views

# Urls
urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Kakao Plus User Skills
    ## Home
    path('skill/user/home', views.GET_UserHome),
    
    ## Order Flow
    path('skill/user/order/get_sellingTime',  views.GET_SellingTime),
    path('skill/user/order/get_menu',         views.GET_Menu),
    path('skill/user/order/get_pickupTime',   views.GET_PickupTime),
    path('skill/user/order/set_orderSheet',   views.SET_OrderSheet),
    path('skill/user/order/post_order',       views.POST_Order),

    ## Order View Flow
    path('skill/user/orderView/get_orderList', views.GET_OrderList),
    path('skill/user/orderView/get_coupon',    views.GET_Coupon),

    ## Order Edit Flow
    path('skill/user/orderEdit/post_orderCancel',     views.POST_OrderCancel),
    path('skill/user/orderEdit/get_confirmUseCoupon', views.GET_ConfirmUserCoupon), 
    path('skill/user/orderEdit/post_useCoupon',       views.POST_UseCoupon),

    ## Order Pickup Time Change Flow
    path('skill/user/orderEdit/get_pickupTimeForChange', views.GET_PickupTimeForChange),
    path('skill/user/orderEdit/set_pickupTimeByChanged', views.SET_PickupTimeByChanged),

    ## ETC
    path('skill/user/etc/get_userManual', views.GET_UserManual),
    path('skill/user/etc/get_userIntro', views.GET_UserIntro),


    # Kakao Plus Partner Skills
    ## Home
    path('skill/partner/home', views.GET_PartnerHome),
    
    ## Order View Flow
    path('skill/partner/orderView/get_orderList', views.GET_StoreOrderList),
    path('skill/partner/orderView/get_calculateCheck', views.GET_CalculateCheck),

    ## ETC
    path('skill/partner/etc/get_partnerManual', views.GET_PartnerManual),
    path('skill/partner/etc/get_partnerIntro', views.GET_PartnerIntro),
]

# Media Link Url
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)