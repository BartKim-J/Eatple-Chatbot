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
from eatple_app.module_kakao.kakaoPay import *
from eatple_app.module_kakao.kakaoBiz import *
from eatple_app.module_kakao.kakao import *
from eatple_app.module_kakao.form import *
from eatple_app.module_kakao.validation import *

# View-System
from eatple_app.views_system.debugger import *

# # # # # # # # # # # # # # # # # # # # # # # # #
#
# Static View
#
# # # # # # # # # # # # # # # # # # # # # # # # #


def kakaoView_Test(user):

    message = "안녕하세요!! 잇플입니다.\n 오늘 잇플은 하루 쉬어 가겠습니다.\n내일은 주문 메시지로 만나게 되길!!"

    KakaoBiz().request(message, '+821045624810')
    KakaoBiz().request(message, '+821057809397')

    kakaoForm = KakaoForm()

    QUICKREPLIES_MAP = [
        {
            'action': 'block',
            'label': '🏠 홈',
            'messageText': KAKAO_EMOJI_LOADING,
            'blockId': KAKAO_BLOCK_USER_HOME,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_GET_MENU
            }
        },
    ]

    thumbnail = {
        'imageUrl': '',
        'fixedRatio': 'true',
        'width': 800,
        'height': 800,
    }

    buttons = [
        {
            'action': 'block',
            'label': '웰컴 블록',
            'messageText': KAKAO_EMOJI_LOADING,
            'blockId': KAKAO_BLOCK_USER_WELCOME,
            'extra': {
            }
        },
        {
            'action': 'block',
            'label': '인증 블록',
            'messageText': KAKAO_EMOJI_LOADING,
            'blockId': KAKAO_BLOCK_USER_SIGNUP,
            'extra': {
            }
        },
    ]

    KakaoInstantForm().Message(
        '테스트 베드 in Server',
        '',
        thumbnail=thumbnail,
        buttons=buttons,
        kakaoForm=kakaoForm
    )

    kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)

    return JsonResponse(kakaoForm.GetForm())

# # # # # # # # # # # # # # # # # # # # # # # # #
#
# External View
#
# # # # # # # # # # # # # # # # # # # # # # # # #


@csrf_exempt
def GET_Test(request):
    EatplusSkillLog('GET_Test')

    try:
        kakaoPayload = KakaoPayLoad(request)

        user = userValidation(kakaoPayload)

        #kakaoPay = KakaoPay()
        # return kakaoPay.PushOrderSheet(user)

        return kakaoView_Test(kakaoPayload)

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView('{}'.format(ex))
