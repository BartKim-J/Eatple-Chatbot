from django.urls import path, include
from django.conf.urls import url

from eatple_app import api

KAKAO_API_URLS = [
    path('kakao/api/oauth', api.GET_KAKAO_Oauth),

    path('kakao/channel/log', api.POST_KAKAO_ChannelLog),

    path('kakao/api/signup', api.GET_KAKAO_Signup),
    path('kakao/api/signup_setup', api.GET_KAKAO_SignupSetup),
    path('kakao/api/signout', api.GET_KAKAO_Signup),
]
