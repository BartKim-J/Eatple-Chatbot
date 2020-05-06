# View-System
from eatple_app.views_system.include import *
from eatple_app.views_system.debugger import *

from eatple_app.views import GET_UserHome

# # # # # # # # # # # # # # # # # # # # # # # # #
#
# Static View
#
# # # # # # # # # # # # # # # # # # # # # # # # #


def getFriendCode(kakaoPayload):
    try:
        param = kakaoPayload.dataActionParams['friend_code']['origin']
        return param.upper()
    except (TypeError, AttributeError, KeyError):
        return None


def kakaoView_FriendCodeSubmit(kakaoPayload):
    kakaoForm = KakaoForm()

    QUICKREPLIES_MAP = [
        {
            'action': 'block',
            'label': '다시 입력하기',
            'messageText': KAKAO_EMOJI_LOADING,
            'blockId': KAKAO_BLOCK_USER_FRIEND_CODE_SUBMIT,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_FRIEND_CODE_SUBMIT
            }
        },
        {
            'action': 'block',
            'label': '건너뛰기',
            'messageText': KAKAO_EMOJI_LOADING,
            'blockId': KAKAO_BLOCK_USER_SUBMIT_LOCATION,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_FRIEND_CODE_SUBMIT
            }
        },
    ]

    # User Validation
    user = userValidation(kakaoPayload)
    if (user == None):
        return errorView('잘못된 사용자 계정', '찾을 수 없는 사용자 계정 아이디입니다.')

    friend_code = getFriendCode(kakaoPayload)
    if(friend_code == user.get_friend_code()):
        KakaoInstantForm().Message(
            '자신의 코드를 등록할 수 없습니다.',
            '코드를 다시 확인해주세요.',
            kakaoForm=kakaoForm
        )
    else:
        status = user.apply_friend_code(friend_code)
        if(friend_code == None or status == False):
            KakaoInstantForm().Message(
                '존재하지 않는 친구 코드입니다.',
                '코드를 다시 확인해주세요.',
                kakaoForm=kakaoForm
            )
        else:
            QUICKREPLIES_MAP = [
                {
                    'action': 'block',
                    'label': '위치 등록하기',
                    'messageText': KAKAO_EMOJI_LOADING,
                    'blockId': KAKAO_BLOCK_USER_EDIT_LOCATION,
                    'extra': {
                        KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_FRIEND_CODE_SUBMIT
                    }
                },
                {
                    'action': 'block',
                    'label': '건너뛰기',
                    'messageText': KAKAO_EMOJI_LOADING,
                    'blockId': KAKAO_BLOCK_USER_GET_STORE,
                    'extra': {
                        KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_FRIEND_CODE_SUBMIT
                    }
                },
            ]

            KakaoInstantForm().Message(
                '친구 코드 입력에 성공하였습니다.',
                '쿠폰은 메뉴 구매시 자동 적용됩니다.',
                kakaoForm=kakaoForm
            )
            KakaoInstantForm().Message(
                '잇플은 위치 기반으로 주변 맛집을 추천해드리고 있습니다.\n\n자주 사용할 위치를 등록해주세요.',
                '패스트파이브 신사점의 경우 신사동으로 핀 위치설정해주세요',
                kakaoForm=kakaoForm
            )

    kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)

    return JsonResponse(kakaoForm.GetForm())


def kakaoView_FriendInvitation(kakaoPayload):
    kakaoForm = KakaoForm()

    QUICKREPLIES_MAP = [
        {
            'action': 'block',
            'label': '🏠  홈',
            'messageText': '🏠  홈',
            'blockId': KAKAO_BLOCK_USER_HOME,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_FRIEND_INVITE
            }
        },
    ]

    # User Validation
    user = userValidation(kakaoPayload)
    if (user == None):
        return errorView('잘못된 사용자 계정', '찾을 수 없는 사용자 계정 아이디입니다.')

    buttons = [
        {
            'action': 'share',
            'label': '공유하기',
            'extra': {},
        },
    ]

    # HEADER
    homeImg = '{}{}'.format(HOST_URL, EATPLE_FRIEND_INVITATION_IMG)

    thumbnail = {
        'imageUrl': homeImg,
        'fixedRatio': 'true',
        'width': 800,
        'height': 800,
    }

    KakaoInstantForm().Message(
        '친구에게 아래 카드를 공유해주세요.',
        '공유 시 2,000원 할인혜택',
        kakaoForm=kakaoForm
    )

    kakaoForm.BasicCard_Push(
        '친구 코드 : {}'.format(user.get_friend_code()),
        '위 친구 코드를 가입할 때 입력해주세요',
        thumbnail,
        buttons
    )

    kakaoForm.BasicCard_Add()

    kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)

    return JsonResponse(kakaoForm.GetForm())


# # # # # # # # # # # # # # # # # # # # # # # # #
#
# External View
#
# # # # # # # # # # # # # # # # # # # # # # # # #


@csrf_exempt
def GET_FriendInvitation(request):
    EatplusSkillLog('GET_FriendInvitation')

    try:
        kakaoPayload = KakaoPayLoad(request)

        # User Validation
        user = userValidation(kakaoPayload)
        if (user == None):
            return GET_UserHome(request)

        return kakaoView_FriendInvitation(kakaoPayload)

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView('{}'.format(ex))


@csrf_exempt
def POST_FriendCodeSubmit(request):
    EatplusSkillLog('POST_FriendCodeSubmit')

    try:
        kakaoPayload = KakaoPayLoad(request)

        # User Validation
        user = userValidation(kakaoPayload)
        if (user == None):
            return GET_UserHome(request)

        return kakaoView_FriendCodeSubmit(kakaoPayload)

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView('{}'.format(ex))
