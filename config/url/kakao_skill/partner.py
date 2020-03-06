from django.urls import path, include
from django.conf.urls import url

from eatple_app import views

KAKAO_SKILL_PARTNER_URLS = [
    # Kakao Plus Partner Skills
    # Home
    path('skill/partner/home', views.GET_PartnerHome),

    # Order View Flow
    path('skill/partner/orderView/get_order_details',
         views.GET_ParnterOrderDetails),
]
