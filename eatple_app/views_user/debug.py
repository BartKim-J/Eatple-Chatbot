# View-System
from eatple_app.views_system.include import *
from eatple_app.views_system.debugger import *

# # # # # # # # # # # # # # # # # # # # # # # # #
#
# Static View
#
# # # # # # # # # # # # # # # # # # # # # # # # #


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

        return kakaoView_Debug(kakaoPayload)

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView('{}'.format(ex))
