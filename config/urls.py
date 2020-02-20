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

from django.views.static import serve

from rest_framework import routers
from rest_framework_swagger.views import get_swagger_view

from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import url

from eatple_app import views
from eatple_app import api
from eatple_app import templates

schema_view = get_swagger_view(title="Eatple Rest API")


if(settings.SETTING_ID == 'DEPLOY'):
    admin.site.site_header = "라이브 서버"
else:
    admin.site.site_header = "개발 서버"

admin.site.index_title = "Dashboard"
admin.site.site_title = "Eat+ Admin"

# Urls
urlpatterns = [
    # Admin
    path('jet/', include('jet.urls', 'jet')),  # Django JET URLS
    path('jet/dashboard/', include('jet.dashboard.urls',
                                   'jet-dashboard')),  # Django JET dashboard URLS
    path('admin/', admin.site.urls),
]

# Dashboard Stie
urlpatterns += {
    path('', templates.dashboard),
    path('404', templates.error404),
    path('sales/dashboard', templates.sales_dashboard),
    path('sales/menu_list', templates.sales_menulist),
}
# Urls - User App
urlpatterns += [
    #Test
    path('skill/user/test', views.GET_Test),
    
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
    path('skill/partner/orderView/get_order_details',
         views.GET_ParnterOrderDetails),
]

# Urls - KAKAO API
urlpatterns += [
    path('kakao/api/oauth', api.GET_KAKAO_Oauth),

    path('kakao/channel/log', api.POST_KAKAO_ChannelLog),

    path('kakao/api/signup', api.GET_KAKAO_Signup),
    path('kakao/api/signup_setup', api.GET_KAKAO_SignupSetup),
    path('kakao/api/signout', api.GET_KAKAO_Signup),
]

# Urls - SLACK API
urlpatterns += [
    url('slack/events', api.Events.as_view()),
]

router = routers.DefaultRouter()
router.register(r'order_validation', api.OrderValidation)
router.register(r'order_information', api.OrderInformation)

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

urlpatterns += [
    url(r'^media/(?P<path>.*)$', serve,
        {'document_root': settings.MEDIA_ROOT}),
    url(r'^static/(?P<path>.*)$', serve,
        {'document_root': settings.STATIC_ROOT}),
]
