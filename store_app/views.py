#Django Library
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

#External Library
import json

#Models
from .models_order import Order
from .models_store import Store, Menu

#View Modules
from .module_KakaoForm import Kakao_SimpleForm, Kakao_CarouselForm

from .views_system import EatplusSkillLog, errorView

from .views_user import userHome, getSellingTime, selectMenu, getPickupTime, orderConfirm, pickupTimeConfirm, getOrderList, getCoupon, orderCancel, orderPickupTimeChange, userManual, getOrderPickupTime
from .views_partner import partnerHome

### API Functions ###
