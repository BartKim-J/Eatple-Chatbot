from django.urls import path, include
from django.conf.urls import url

from eatple_app import api

KAKAO_PAY_API_URLS = [
    path('order/approve', api.GET_KAKAO_PAY_OrderApprove),
    path('order/ordersheet', api.GET_KAKAO_PAY_OrderSheet),
    path('order/status', api.GET_KAKAO_PAY_OrderStatus),

    path('payment/approve', api.GET_KAKAO_PAY_PaymentApprove),
]

KAKAO_OPTION_API_URLS = [
    path('order/option/choice', api.POST_KAKAO_OPTION_OptionChoice),
    path('order/option/check', api.GET_KAKAO_OPTION_OptionCheck),

]


KAKAO_API_URLS = [
    path('kakao/api/oauth', api.GET_KAKAO_Oauth),

    path('kakao/channel/log', api.POST_KAKAO_ChannelLog),

    path('kakao/api/signup', api.GET_KAKAO_Signup),
    path('kakao/api/signup_setup', api.GET_KAKAO_SignupSetup),
    path('kakao/api/signout', api.GET_KAKAO_Signup),
]
