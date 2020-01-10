# Django Library
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

# Models
from eatple_app.models import *

# Define
from eatple_app.define import *

# Modules
from eatple_app.module_kakao.reponseForm import *
from eatple_app.module_kakao.requestForm import *
from eatple_app.module_kakao.validation import *

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

# # # # # # # # # # # # # # # # # # # # # # # # #
#
# Static View
#
# # # # # # # # # # # # # # # # # # # # # # # # #

def orderCheckTimeValidation():
    currentDate = dateNowByTimeZone()
    currentDateWithoutTime = currentDate.replace(hour=0, minute=0, second=0, microsecond=0)

    # Time QA DEBUG
    # currentDate = currentDate.replace(hour=13, minute=31, second=0, microsecond=0)
    # currentDateWithoutTime = currentDate.replace(hour=0, minute=0, second=0, microsecond=0)

    # Prev Lunch Order Time 10:30 ~ 14:00
    lunchCheckTimeStart = currentDateWithoutTime + datetime.timedelta(hours=10, minutes=30, days=-1)
    lunchCheckTimeEnd = currentDateWithoutTime + datetime.timedelta(hours=14, minutes=0)

    # Dinner Order Time 17:30 ~ 21:0
    dinnerCheckTimeStart = currentDateWithoutTime + datetime.timedelta(hours=17, minutes=30)
    dinnerCheckTimeEnd = currentDateWithoutTime + datetime.timedelta(hours=21, minutes=0)
    
    if(lunchCheckTimeStart < currentDate) and (currentDate < lunchCheckTimeEnd):
        return True

    if(dinnerCheckTimeStart < currentDate) and (currentDate < dinnerCheckTimeEnd):
        # return True
        return False
    
    return False

def kakaoView_OrderDetails(kakaoPayload):
    # Partner Validation
    partner = partnerValidation(kakaoPayload)
    if (partner == None):
        return errorView('Invalid Block Access', '정상적이지 않은 경로거나, 잘못된 계정입니다.')

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

    if(orderCheckTimeValidation()):
        
        orderManager = PartnerOrderManager(partner)
        orderManager.orderPaidCheck()
        
        availableOrders = orderManager.getAvailableOrders()
        
        if availableOrders:        
            totalOrder = 0
            kakaoForm = KakaoForm()
            
            refOrder = availableOrders[0]
            totalCount = availableOrders.count()
            
            pickupTimes = refOrder.menu.pickup_time.all()
            
            header = {
                'title': '총 {sellingTime} 주문량은 {count}개 입니다.'.format(
                    sellingTime=dict(SELLING_TIME_CATEGORY)[refOrder.menu.selling_time], 
                    count=totalCount
                ),
                'imageUrl': '{}{}'.format(HOST_URL, '/media/STORE_DB/images/default/partnerOrderSheet.png'),
            }
            
            
            imageUrl = '{}{}'.format(HOST_URL, refOrder.menu.imgURL())

            for pickupTime in pickupTimes:
                refPickupTime = refOrder.pickupTimeToDateTime(str(pickupTime.time))
                
                orderByPickupTime = availableOrders.filter(pickup_time=refPickupTime)
                orderCount = orderByPickupTime.count()
                
                if(orderCount > 0):
                    kakaoForm.ListCard_Push(
                        '{pickupTime} - [ {count}개 ]'.format(
                            pickupTime=refPickupTime.strftime('%p %I시 %M분').replace('AM','오전').replace('PM','오후'),
                            count=orderCount
                        ),
                        '{menu}'.format(menu=refOrder.menu.name),
                        imageUrl, 
                        None
                    )
                
            kakaoForm.ListCard_Add(header)
                
        else:
            kakaoForm = KakaoForm()

            kakaoForm.SimpleText_Add('오늘은 들어온 주문이 없어요!')
    else:
        kakaoForm = KakaoForm()

        kakaoForm.BasicCard_Push(
            '아직 주문조회 가능시간이 아닙니다.', 
            ' 점심 주문조회 가능시간\n - 오전 10시 30분 ~ 오후 2시', 
            {}, 
            []
        )
        
        kakaoForm.BasicCard_Add()
        
    kakaoForm.QuickReplies_AddWithMap(ORDER_LIST_QUICKREPLIES_MAP)
    
    return JsonResponse(kakaoForm.GetForm())

# @TODO
def kakaoView_CalculateDetails(kakaoPaylaod):
    
    # Partner Validation
    partner = partnerValidation(kakaoPayload)
    if (partner == None):
        return errorView('Invalid Block Access', '정상적이지 않은 경로거나, 잘못된 계정입니다.')

    return errorView('{}'.format(ex))


# # # # # # # # # # # # # # # # # # # # # # # # #
#
# External View
#
# # # # # # # # # # # # # # # # # # # # # # # # #

@csrf_exempt
def GET_ParnterOrderDetails(request):
    EatplusSkillLog('GET_ParnterOrderDetails')
    try:
        kakaoPayload = KakaoPayLoad(request)
        
        # User Validation
        partner = partnerValidation(kakaoPayload)
        if (partner == None):
            return GET_PartnerHome(request)
        
        return kakaoView_OrderDetails(kakaoPayload)

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView('{} '.format(ex))

@csrf_exempt
def GET_CalculateDetails(request):
    EatplusSkillLog('GET_CalculateDetails')
    try:
        kakaoPayload = KakaoPayLoad(request)
        
        # User Validation
        partner = partnerValidation(kakaoPayload)
        if (partner == None):
            return GET_PartnerHome(request)
        
        return kakaoView_CalculateDetails(kakaoPayload)

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView('{} '.format(ex))



