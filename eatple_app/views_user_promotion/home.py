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


# # # # # # # # # # # # # # # # # # # # # # # # #
#
# Static View
#
# # # # # # # # # # # # # # # # # # # # # # # # #

def kakaoView_MenuListup(kakaoPayload):
    # User Validation
    user = userValidation(kakaoPayload)
    if (user == None):
        return GET_UserHome(request)

    # User's Eatple Pass Validation
    eatplePassStatus = eatplePassValidation(user)
    if(eatplePassStatus != None):
        return eatplePassStatus
    
    sellingTime = sellingTimeCheck()

    # Order Log Record
    orderRecordSheet = OrderRecordSheet()
    orderRecordSheet.user = user
    orderRecordSheet.recordUpdate(ORDER_RECORD_GET_MENU)

    if (sellingTime == None):
        return errorView('Get Invalid Selling Time', '잘못된 주문 시간입니다.')
    elif sellingTime == SELLING_TIME_DINNER:
        '''
            @NOTE Dinner Time Close In Alpha 
        '''
        
        return errorView('Get Invalid Selling Time', '오늘 점심은 이미 마감되었어요.\n내일 점심을 기대해주세요.')


    menuList = Menu.objects.filter(sellingTime=sellingTime, store__type=STORE_TYPE_NORMAL)[:MENU_LIST_LENGTH]

    if menuList:
        kakaoForm = KakaoForm()

        # Menu Carousel Card Add
        for menu in menuList:
            imageUrl = '{}{}'.format(HOST_URL, menu.imgURL())
            
            thumbnail = {
                'imageUrl': imageUrl,
                'fixedRatio': 'true',
                'width': 800,
                'height': 800,
            }

            kakaoMapUrl = 'https://map.kakao.com/link/map/{},{}'.format(
                menu.store.name, menu.store.latlng)

            buttons = [
                {
                    'action': 'block',
                    'label': '주문하기',
                    'messageText': '로딩중..',
                    'blockId': KAKAO_BLOCK_USER_SET_PICKUP_TIME,
                    'extra': {
                        KAKAO_PARAM_STORE_ID: menu.store.store_id,
                        KAKAO_PARAM_MENU_ID: menu.menu_id,
                        KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_GET_MENU
                    }
                },
                {
                    'action': 'webLink',
                    'label': '위치보기',
                    'webLinkUrl': kakaoMapUrl
                },
            ]

            kakaoForm.BasicCard_Push(
                '{}'.format(menu.name), 
                '{}'.format(menu.store.name), 
                thumbnail, 
                buttons
            )
            
        kakaoForm.BasicCard_Add()
    
    else:
        kakaoForm = KakaoForm()

        kakaoForm.SimpleText_Add('판매중인 메뉴가 없어요...')

    QUICKREPLIES_MAP = [
        {
            'action': 'block',
            'label': '홈으로 돌아가기',
            'messageText': '로딩중..',
            'blockId': KAKAO_BLOCK_USER_HOME,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_GET_MENU
            }
        },
    ]

    kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)       

    return JsonResponse(kakaoForm.GetForm())


# # # # # # # # # # # # # # # # # # # # # # # # #
#
# External View
#
# # # # # # # # # # # # # # # # # # # # # # # # #
@csrf_exempt
def GET_ProMotionHome(request):
    EatplusSkillLog('Get Menu')

    try:
        kakaoPayload = KakaoPayLoad(request)
        return kakaoView_MenuListup(kakaoPayload)
    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView('{}'.format(ex))
