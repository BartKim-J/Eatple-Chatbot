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
        'action': 'block',
        'label': '홈으로 돌아가기',
        'messageText': '로딩중..',
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
            'action': 'block',
            'label': '새로고침',
            'messageText': '로딩중..',
            'blockId': KAKAO_BLOCK_PARTNER_GET_ORDER_DETAILS,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_PARTNER_GET_ORDER_DETAILS
            }
        },
        {
            'action': 'block',
            'label': '홈으로 돌아가기',
            'messageText': '로딩중..',
            'blockId': KAKAO_BLOCK_PARTNER_HOME,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_PARTNER_GET_ORDER_DETAILS
            }
        },
    ]

    orderManager = PartnerOrderManager(partner)
    orderManager.orderPaidCheck()
    
    availableOrders = orderManager.getAvailableOrders()
    
    if availableOrders:        
        totalOrder = 0
        kakaoForm = KakaoForm()
        
        refOrder = availableOrders[0]
        totalCount = availableOrders.count()
        
        pickupTimes = refOrder.menu.pickupTime.all()
        
        header = {
            'title': '총 {sellingTime} 주문량은 {count}개 입니다.'.format(
                sellingTime=dict(SELLING_TIME_CATEGORY)[refOrder.menu.sellingTime], 
                count=totalCount
            ),
            'imageUrl': '{}{}'.format(HOST_URL, '/media/STORE_DB/images/default/partnerOrderSheet.png'),
        }
        
        
        imageUrl = '{}{}'.format(HOST_URL, refOrder.menu.imgURL())

        for pickupTime in pickupTimes:
            pickup_time = refOrder.pickupTimeToDateTime(str(pickupTime.time))
            
            orderByPickupTime = availableOrders.filter(pickup_time=pickup_time)
            orderCount = orderByPickupTime.count()
            
            if(orderCount > 0):
                kakaoForm.ListCard_Push(
                    '{pickupTime} - [ {count}개 ]'.format(
                        pickupTime=pickup_time.strftime('%p %I시 %M분').replace('AM','오전').replace('PM','오후'),
                        count=orderCount
                    ),
                    '{menu}'.format(menu=refOrder.menu.name),
                    imageUrl, 
                    None
                )
            
        kakaoForm.ListCard_Add(header)
            
    else:
        kakaoForm = KakaoForm()

        kakaoForm.SimpleText_Add('아직 들어온 주문이 없어요!')
        
    kakaoForm.QuickReplies_AddWithMap(ORDER_LIST_QUICKREPLIES_MAP)
    
    return JsonResponse(kakaoForm.GetForm())

# # # # # # # # # # # # # # # # # # # # # # # # #
#
# External View
#
# # # # # # # # # # # # # # # # # # # # # # # # #

@csrf_exempt
def GET_ParnterOrderDetails(request):
    EatplusSkillLog('GET_OrderDetails')
    try:
        kakaoPayload = KakaoPayLoad(request)
        return kakaoView_OrderDetails(kakaoPayload)

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView('{} '.format(ex))

@csrf_exempt
def GET_A(request):
    EatplusSkillLog('GET_OrderDetails')
    try:
        kakaoPayload = KakaoPayLoad(request)
        return kakaoView_OrderDetails(kakaoPayload)

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView('{} '.format(ex))



