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
from django.urls import path, include

from rest_framework import routers
from rest_framework_swagger.views import get_swagger_view

from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import url

from eatple_app import views

schema_view = get_swagger_view(title="Eatple Rest API")

# Urls
urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
]

# Urls - User App
urlpatterns += [
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
]

# Urls - Events App
urlpatterns += [
    # Home
    path('skill/promotion/home', views.GET_ProMotionHome),
]

# Urls - Partner App
urlpatterns += [
    # Kakao Plus Partner Skills
    # Home
    path('skill/partner/home', views.GET_PartnerHome),
    
    # Order View Flow
    path('skill/partner/orderView/get_order_details', views.GET_ParnterOrderDetails),
]

# Urls - KAKAO API
urlpatterns += [
    path('kakao/auth/leave', views.POST_KAKAO_Leave),
    path('kakao/channel/log', views.POST_KAKAO_ChannelLog)
]

# Urls - SLACK API
urlpatterns += [
    url('slack/events', views.Events.as_view()),
]

router = routers.DefaultRouter()
router.register(r'order_validation', views.OrderValidation)

# Urls - REST API
urlpatterns += [
    path('api/', include(router.urls)),
]


urlpatterns += [
    path('api/doc', schema_view),
]

# Media Link Url
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
