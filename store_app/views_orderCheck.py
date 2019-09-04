#Django Library
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

#External Library
import requests
import json

#Models 
from .models_config import Config

from .models_user  import User
from .models_order import Order
from .models_store import Store, Menu, Category, SubCategory

#View Modules
from .module_KakaoForm import Kakao_SimpleForm, Kakao_CarouselForm, KakaoPayLoad

#View
from .views_kakaoTool import getLatLng
from .views_system import EatplusSkillLog, errorView

ORDER_LIST_LENGTH = 5

def OrderListup(name):
    ORDER_LIST_QUICKREPLIES_MAP = [                
        {'action': "message", 'label': "홈으로 돌아가기",    'messageText': "홈으로 돌아가기", 'blockid': "none", 
         'extra': { Config.KAKAO_EXTRA_STATUS: Config.KAKAO_EXTRA_STATUS_OK }},
        {'action': "message", 'label': "새로고침",    'messageText': "식권 조회", 'blockid': "none", 
         'extra': { Config.KAKAO_EXTRA_STATUS: Config.KAKAO_EXTRA_STATUS_OK }},
    ]

    OrderList = Order.objects.filter(userInstance__name=name)[:ORDER_LIST_LENGTH]
    if OrderList:
        KakaoForm = Kakao_CarouselForm()
        KakaoForm.BasicCard_Init()

        for order in OrderList:
            thumbnail = { "imageUrl": "" }

            kakaoMapUrl = "https://map.kakao.com/link/map/{},{}".format(order.storeInstance.name, getLatLng(order.storeInstance.addr))

            if( Config.ORDER_STATUS_DICT[order.status] < Config.ORDER_STATUS_DICT['픽업 준비중']
            ):
                buttons = [
                    {'action': "webLink", 'label': "위치보기",  "webLinkUrl": kakaoMapUrl},
                    {'action': "message", 'label': "결제 취소 하기",  'messageText': "결제 취소 하기", 'extra': { }}
                ]
            else:
                buttons = [
                    {'action': "webLink", 'label': "위치보기",  "webLinkUrl": kakaoMapUrl},
                ]

            KakaoForm.BasicCard_Add(
                "주문번호: {}".format(order.management_code),
                " - 주문자: {}\n\n - 매장: {} \n - 메뉴: {}\n\n - 결제 금액: {}원\n - 픽업 시간: {}\n\n - 주문 상태: {}".format(
                    order.userInstance.name,
                    order.storeInstance.name, 
                    order.menuInstance.name, 
                    order.menuInstance.price, 
                    "11:30",
                    order.status
                ),
                thumbnail, buttons
            )

    else:
        KakaoForm = Kakao_SimpleForm()
        KakaoForm.SimpleForm_Init()


        KakaoForm.SimpleText_Add("주문 내역이 존재하지 않습니다.")

    for entryPoint in ORDER_LIST_QUICKREPLIES_MAP:
        KakaoForm.QuickReplies_Add(entryPoint['action'], entryPoint['label'], entryPoint['messageText'], entryPoint['blockid'], entryPoint['extra'])

    return JsonResponse(KakaoForm.GetForm())


@csrf_exempt
def getOrderList(request):
    try:
        kakaoPayload = KakaoPayLoad(request)

        EatplusSkillLog("Order Check Flow", "Get Order List")

        return OrderListup("잇플")

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView("Get Order List Error\n- {} ".format(ex))



