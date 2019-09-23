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
from .module_KakaoForm import Kakao_SimpleForm, Kakao_CarouselForm

#View
from .views_kakaoTool import getLatLng, KakaoPayLoad
from .views_system import EatplusSkillLog, errorView
from .views_wording import wordings

#GLOBAL DEFINE
HOST_URL                    = Config.HOST_URL
NOT_APPLICABLE              = Config.NOT_APPLICABLE

ORDER_STATUS                = Config.ORDER_STATUS
ORDER_STATUS_DICT           = Config.ORDER_STATUS_DICT

KAKAO_PARAM_USER_ID         = Config.KAKAO_PARAM_USER_ID
KAKAO_PARAM_ORDER_ID        = Config.KAKAO_PARAM_ORDER_ID
KAKAO_PARAM_STORE_ID        = Config.KAKAO_PARAM_STORE_ID
KAKAO_PARAM_MENU_ID         = Config.KAKAO_PARAM_MENU_ID

KAKAO_PARAM_STATUS          = Config.KAKAO_PARAM_STATUS
KAKAO_PARAM_STATUS_OK       = Config.KAKAO_PARAM_STATUS_OK
KAKAO_PARAM_STATUS_NOT_OK   = Config.KAKAO_PARAM_STATUS_NOT_OK


# # # # # # # # # # # # # # # # # # # # # # # # #
#
# Static View
#
# # # # # # # # # # # # # # # # # # # # # # # # #
DEFAULT_QUICKREPLIES_MAP = [                
    {'action': "message", 'label': wordings.RETURN_HOME_QUICK_REPLISE, 'messageText': wordings.RETURN_HOME_QUICK_REPLISE, 'blockid': "none", 
        'extra': { KAKAO_PARAM_STATUS: KAKAO_PARAM_STATUS_OK }},
]

# # # # # # # # # # # # # # # # # # # # # # # # #
#
# External View
#
# # # # # # # # # # # # # # # # # # # # # # # # #
USER_MANUAL_MAP = [
    {'title': "주문은 어떻게 하나요? ", 'description': "주문하기 클릭 후, 점심 또는 저녁을 선택해주세요. "},
    {'title': "주문 가능한 시간은 언제인가요?", 'description': "점심:전날 16:30~ 당일 10:30 /저녁:당일 10:30~16:30"},
    {'title': "메뉴선택은 어떻게 하나요?", 'description': "점심/저녁을 선택한 후, 먹고싶은 식당의 메뉴를 골라주세요. "},
    {'title': "결제는 어디서하나요?", 'description': "픽업시간에 맞춰 식당에 가셔서 ‘주문상태확인' 버튼을 눌러 식권을 보여주시고 사용하기 버튼을 눌러주세요."},
    {'title': "식당에서 어떻게 픽업할 수 있나요?", 'description': "결제 완료 후 매장 픽업대에서 이름과 휴대전화 뒷번호를 말씀해주세요."},
    {'title': "주문취소/픽업 시간변경이 가능한가요?", 'description': "점심은 당일 09:30까지, 저녁은 당일 15:30까지 주문취소 / 픽업시간변경 버튼을 통해 가능해요"},
    {'title': "잇플에 궁금한 점이 생겼어요!", 'description': "문의사항이 있는 경우에는 ‘상담원으로 전환하기’를 누르신 후 카카오톡으로 말씀해주세요."},
]

USER_MANUAL_MAP = [
    {'title': "한 끼 식사가 매일 5,500원!", 'description': "내가 평소 자주가던 식당의 메뉴들을 5,500원에 즐길 수 있어요!"},
    {'title': "잇플로 시간도 절약하세요.", 'description': "미리 주문하고 픽업시간을 예약하여 기다림없이 맛있는 식사를!"},
    {'title': "가성비 있는 식사가 가능해집니다.", 'description': "꼼꼼하게 검수한 음식만을 제공하며, 다양한 식사를 선택할 수 있어요."},
    {'title': "식사에 가치를 더하다, 잇플", 'description': "평범했던 식사시간에 의미를 더하는 잇플과 새로운 가치를 찾아보세요! "},
]


'''
    @name orderPickupTimeChange
    @param name

    @note
    @bug
    @tood
'''
@csrf_exempt
def userManual(request):
    try:
        kakaoPayload = KakaoPayLoad(request)

        # Invalied Path Access
        #if (kakaoPayload.orderID == NOT_APPLICABLE) or kakaoPayload.pickupTime == NOT_APPLICABLE:
        #    
        #else:
        #    

        EatplusSkillLog("User Manual Flow")

        KakaoForm = Kakao_CarouselForm()
        KakaoForm.BasicCard_Init()

        thumbnail = { "imageUrl": "{}{}".format(HOST_URL, '/media/STORE_DB/images/default/defaultImg.png') }

        buttons = [
            # No Buttons
        ]

        for entryPoint in USER_MANUAL_MAP:
            KakaoForm.BasicCard_Add(entryPoint['title'], entryPoint['description'], thumbnail, buttons)

        for entryPoint in DEFAULT_QUICKREPLIES_MAP:
            KakaoForm.QuickReplies_Add(entryPoint['action'], entryPoint['label'], entryPoint['messageText'], entryPoint['blockid'], entryPoint['extra'])
        
        return JsonResponse(KakaoForm.GetForm())
  
    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView("{}".format(ex))




