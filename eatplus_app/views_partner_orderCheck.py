#Django Library
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

#External Library
import requests
import json

#Models 
from .eatplus_define import EP_define

from .models_user  import User
from .models_order import Order
from .models_store import Store, Menu, Category, SubCategory

#View Modules
from .module_KakaoForm import Kakao_SimpleForm, Kakao_CarouselForm

#View
from .views_kakaoTool import getLatLng, KakaoPayLoad
from .views_system import EatplusSkillLog, errorView

#GLOBAL EP_define
NOT_APPLICABLE              = EP_define.NOT_APPLICABLE

ORDER_STATUS                = EP_define.ORDER_STATUS
ORDER_STATUS_DICT           = EP_define.ORDER_STATUS_DICT

KAKAO_PARAM_ORDER_ID        = EP_define.KAKAO_PARAM_ORDER_ID
KAKAO_PARAM_STORE_ID        = EP_define.KAKAO_PARAM_STORE_ID
KAKAO_PARAM_MENU_ID         = EP_define.KAKAO_PARAM_MENU_ID

KAKAO_PARAM_STATUS          = EP_define.KAKAO_PARAM_STATUS
KAKAO_PARAM_STATUS_OK       = EP_define.KAKAO_PARAM_STATUS_OK
KAKAO_PARAM_STATUS_NOT_OK   = EP_define.KAKAO_PARAM_STATUS_NOT_OK
