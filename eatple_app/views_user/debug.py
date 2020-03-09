# Django Library
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

# Models
from eatple_app.models import *

# Define
from eatple_app.define import *

# Modules
from eatple_app.module_kakao.responseForm import *
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


def kakaoView_DebugKakaoPay(kakaoPayload):
    """
        Default Variable Define
    """
    # User Validation
    user = userValidation(kakaoPayload)
    if (user == None):
        return errorView('잘못된 사용자 계정', '찾을 수 없는 사용자 계정 아이디입니다.')

    kakaoResponse = KakaoPay().PushOrderSheet(
        user,
        'EP000D871E1673',
        '오징어 덮밥',
        '0032',
        6000
    )

    """
        KAKAO I Dev Test Bed
    """
    kakaoForm = KakaoForm()

    QUICKREPLIES_MAP = [
        {
            'action': 'block',
            'label': '새로고침',
            'messageText': KAKAO_EMOJI_LOADING,
            'blockId': KAKAO_BLOCK_USER_TEST_BED,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_TEST_BED
            }
        },
    ]

    if(kakaoResponse.status_code == status.HTTP_400_BAD_REQUEST):
        body = json.loads(kakaoResponse.text)

        KakaoInstantForm().Message(
            '카카오 페이 에러',
            '코드 : {}\n메세지 : {}'.format(
                body['code'],
                body['msg']
            ),
            kakaoForm=kakaoForm
        )
    elif(kakaoResponse.status_code != status.HTTP_400_BAD_REQUEST):
        body = json.loads(kakaoResponse.text)

        oneclick_url = 'kakaotalk://bizplugin?plugin_id={api_id}&oneclick_id={order_id}'.format(
            api_id=KAKAO_PAY_ONE_CLICK_API_ID,
            order_id=body["tid"]
        )

        buttons = [
            {
                'action': 'osLink',
                'label': '원클릭 결제하기',
                'messageText': KAKAO_EMOJI_LOADING,
                'osLink': {
                    'android': oneclick_url,
                    'ios': oneclick_url,
                },
            },
        ]

        KakaoInstantForm().Message(
            '메뉴 결정이 완료되었습니다.',
            '',
            buttons=buttons,
            kakaoForm=kakaoForm
        )

    kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)

    return JsonResponse(kakaoForm.GetForm())


def kakaoView_Debug(kakaoPayload):
    """
        Default Variable Define
    """
    # User Validation
    user = userValidation(kakaoPayload)
    if (user == None):
        return errorView('잘못된 사용자 계정', '찾을 수 없는 사용자 계정 아이디입니다.')

    """
        Kakao API Test Bed
    """
    # message = "안녕하세요!! 잇플입니다.\n 오늘 잇플은 하루 쉬어 가겠습니다.\n내일은 주문 메시지로 만나게 되길!!"
    # KakaoBiz().request(message, '+821057809397')

    """
        KAKAO I Dev Test Bed
    """
    kakaoForm = KakaoForm()

    QUICKREPLIES_MAP = [
        {
            'action': 'block',
            'label': '새로고침',
            'messageText': KAKAO_EMOJI_LOADING,
            'blockId': KAKAO_BLOCK_USER_TEST_BED,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_TEST_BED
            }
        },
    ]

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
        '테스트 베드',
        '',
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
def GET_Debug(request):
    EatplusSkillLog('GET_TestBed')

    try:
        kakaoPayload = KakaoPayLoad(request)

        user = userValidation(kakaoPayload)

        return kakaoView_DebugKakaoPay(kakaoPayload)

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView('{}'.format(ex))
