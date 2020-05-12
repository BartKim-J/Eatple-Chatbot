# View-System
from eatple_app.views_system.include import *
from eatple_app.views_system.debugger import *

from eatple_app.views import GET_UserHome

# # # # # # # # # # # # # # # # # # # # # # # # #
#
# Static View
#
# # # # # # # # # # # # # # # # # # # # # # # # #


def getDeliveryAddress(kakaoPayload):
    try:
        address = kakaoPayload.dataActionParams['address']['origin']
        try:
            address = int(address)
        except:
            address = kakaoPayload.dataActionParams['address']['origin']

        return address
    except (TypeError, AttributeError, KeyError):
        return None


def kakaoViewDeliveryAddressSubmit(kakaoPayload):
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

    ]

    # User Validation
    user = userValidation(kakaoPayload)
    if (user == None):
        return errorView('잘못된 사용자 계정', '찾을 수 없는 사용자 계정 아이디입니다.')

    address = getDeliveryAddress(kakaoPayload)
    if(address == None):
        KakaoInstantForm().Message(
            '알 수 없는 입력입니다.',
            '입력된 값: {}'.format(
                kakaoPayload.dataActionParams['address']['origin']
            ),
            kakaoForm=kakaoForm
        )
    else:
        KakaoInstantForm().Message(
            '사무실 등록이 완료되었습니다.',
            '이후 픽업존 메뉴 주문시 사무실로 배달됩니다.',
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
def POST_DeliveryAddressSubmit(request):
    EatplusSkillLog('POST_DeliveryAddressSubmit')

    try:
        kakaoPayload = KakaoPayLoad(request)

        # User Validation
        user = userValidation(kakaoPayload)
        if (user == None):
            return GET_UserHome(request)

        return kakaoViewDeliveryAddressSubmit(kakaoPayload)

    except (RuntimeError, TypeError, NameError, KeyError) as ex:
        return errorView('{}'.format(ex))
