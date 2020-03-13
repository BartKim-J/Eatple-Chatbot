# View-System
from eatple_app.views_system.include import *
from eatple_app.views_system.debugger import *


DEFAULT_QUICKREPLIES_MAP = [
    {
        'action': 'block',
        'label': '🏠  홈',
        'messageText': KAKAO_EMOJI_LOADING,
        'blockId': KAKAO_BLOCK_USER_HOME,
        'extra': {}
    },
]

# # # # # # # # # # # # # # # # # # # # # # # # #
#
# Static View
#
# # # # # # # # # # # # # # # # # # # # # # # # #


def kakaoView_notifiy(kakaoPayload):
    kakaoForm = KakaoForm()

    QUICKREPLIES_MAP = [
        {
            'action': 'block',
            'label': '🏠  홈',
            'messageText': KAKAO_EMOJI_LOADING,
            'blockId': KAKAO_BLOCK_USER_HOME,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_GET_MENU
            }
        },
    ]

    # User Validation
    user = userValidation(kakaoPayload)
    if (user == None):
        return errorView('잘못된 블럭 경로', '정상적이지 않은 경로거나, 잘못된 계정입니다.')

    header = {
        'title': '공지사항',
        'imageUrl': '{}{}'.format(HOST_URL, PARTNER_ORDER_SHEET_IMG),
    }
    kakaoForm.ListCard_Push(
        '신사 지역 점포들이 오픈되었습니다.',
        '2020.03.11',
        None,
        None
    )
    kakaoForm.ListCard_Push(
        '카카오 페이 결제가 추가되었습니다.',
        '2020.03.10',
        None,
        None
    )
    kakaoForm.ListCard_Add(header)

    kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)

    return JsonResponse(kakaoForm.GetForm())


# # # # # # # # # # # # # # # # # # # # # # # # #
#
# External View
#
# # # # # # # # # # # # # # # # # # # # # # # # #


@csrf_exempt
def GET_UserNotify(request):
    EatplusSkillLog('GET_UserNotify')

    try:
        kakaoPayload = KakaoPayLoad(request)

        # User Validation
        user = userValidation(kakaoPayload)
        if (user == None):
            return GET_UserHome(request)

        return kakaoView_notifiy(kakaoPayload)

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView('{} '.format(ex))
