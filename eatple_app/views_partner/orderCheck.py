# Django Library
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

# Models
from eatple_app.models import *

# Define
from eatple_app.define import *

# Modules
from eatple_app.module_kakao.ReponseForm import *
from eatple_app.module_kakao.RequestForm import *
from eatple_app.module_kakao.Validation import *

# View-System
from eatple_app.views_system.debugger import *

from eatple_app.views import *


DEFAULT_QUICKREPLIES_MAP = [
    {
        'action': "block",
        'label': "홈으로 돌아가기",
        'messageText': "로딩중..",
        'blockId': KAKAO_BLOCK_USER_HOME,
        'extra': {}
    },
]


# STATIC EP_define
ORDER_LIST_LENGTH = 10

# # # # # # # # # # # # # # # # # # # # # # # # #
#
# Static View
#
# # # # # # # # # # # # # # # # # # # # # # # # #

def kakaoView_OrderDetails(kakaoPayload):
    # User Validation
    partner = partnerValidation(kakaoPayload)
    if (partner == None):
        return GET_PartnerHome(request)

    ORDER_LIST_QUICKREPLIES_MAP = [
        {
            'action': "block",
            'label': "새로고침",
            'messageText': "로딩중..",
            'blockId': KAKAO_BLOCK_PARTNER_GET_ORDER_DETAILS,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_PARTNER_GET_ORDER_DETAILS
            }
        },
        {
            'action': "block",
            'label': "홈으로 돌아가기",
            'messageText': "로딩중..",
            'blockId': KAKAO_BLOCK_PARTNER_HOME,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_PARTNER_GET_ORDER_DETAILS
            }
        },
    ]

    orderManager = PartnerOrderManager(partner)
    orderManager.orderPaidCheck()
    
    availableOrders = orderManager.getAvailableOrders()[:ORDER_LIST_LENGTH]

    pickupTimes = PickupTime.objects.filter(store=partner.store)

    if availableOrders:
        kakaoForm = KakaoForm()

        # Total Count
        for order in availableOrders:            
            header = {
                "title": "오늘 총 주문량은 {count}개 입니다.".format(count=1),
                "imageUrl": "{}{}".format(HOST_URL, "/media/STORE_DB/images/default/partnerOrderSheet.png"),
            }
            
            print(order.pickup_time)
            
            imageUrl = "{}{}".format(HOST_URL, order.store.logoImgURL())

            kakaoForm.ListCard_Push(
                "{}-{}".format(order.menu.name, str(order.ordersheet.user.phone_number)[9:13]),
                "{}".format(                    
                    dateByTimeZone(order.pickup_time).strftime('%p %-I시 %-M분 - %m월%d일').replace('AM','오전').replace('PM','오후') ,
                ),
                imageUrl, 
                None
            )
            
            kakaoForm.ListCard_Add(header)
            
        for pickupTime in pickupTimes:
            orderByPickupTime = orderManager.orderListByPickupTime(pickupTime.time)
            
            for order in orderByPickupTime:
                header = {
                    "title": "주문량은 {count}개 입니다.".format(count=1),
                    "imageUrl": "{}{}".format(HOST_URL, "/media/STORE_DB/images/default/partnerOrderSheet.png"),
                }

                imageUrl = "{}{}".format(HOST_URL, order.store.logoImgURL())

                kakaoForm.ListCard_Push(
                    "{}-{}".format(order.menu.name,
                                str(order.ordersheet.user.phone_number)[9:13]),
                    "{}".format(
                        dateByTimeZone(order.pickup_time).strftime(
                            '%p %-I시 %-M분 - %m월%d일').replace('AM', '오전').replace('PM', '오후'),
                    ),
                    imageUrl,
                    None
                )

                kakaoForm.ListCard_Add(header)
            
            
    else:
        kakaoForm = KakaoForm()

        ORDER_LIST_QUICKREPLIES_MAP.insert(0,
            {
                'action': "block",
                'label': "메뉴보기",
                'messageText': "로딩중..",
                'blockId': KAKAO_BLOCK_USER_GET_MENU,
                'extra': {
                    KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_ORDER_DETAILS
                }
            }
        )

        kakaoForm.SimpleText_Add("최근 주문 내역이 존재하지 않습니다!\n주문하시려면 아래 [메뉴보기]를 눌러주세요!")

    kakaoForm.QuickReplies_AddWithMap(ORDER_LIST_QUICKREPLIES_MAP)
    
    return JsonResponse(kakaoForm.GetForm())

# # # # # # # # # # # # # # # # # # # # # # # # #
#
# External View
#
# # # # # # # # # # # # # # # # # # # # # # # # #

@csrf_exempt
def GET_ParnterOrderDetails(request):
    EatplusSkillLog("GET_OrderDetails")
    try:
        kakaoPayload = KakaoPayLoad(request)
        return kakaoView_OrderDetails(kakaoPayload)

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView("{} ".format(ex))

