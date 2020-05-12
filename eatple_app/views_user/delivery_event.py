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
            address = None

        return address
    except (TypeError, AttributeError, KeyError):
        return None


def kakaoViewDeliveryAddressSubmit(kakaoPayload):
    kakaoForm = KakaoForm()

    QUICKREPLIES_MAP = [
        {
            'action': 'block',
            'label': '🏠  홈',
            'messageText': '🏠  홈',
            'blockId': KAKAO_BLOCK_USER_HOME,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_DELIVERY_ADDRESS_SUBMIT
            }
        },
        {
            'action': 'block',
            'label': '주문하러 가기',
            'messageText': '주문하러 가기',
            'blockId': KAKAO_BLOCK_USER_GET_STORE,
            'extra': {
                KAKAO_PARAM_SELLING_TIME: SELLING_TIME_LUNCH,
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_HOME
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
        if(sellingTimeCheck() == None and sellingTimeCheck(True) == SELLING_TIME_DINNER):
            KakaoInstantForm().Message(
                '배달 준비중일때는 등록 및 변경이 불가능합니다.',
                '오전 11시부터 오후 2시까지 등록 및 변경 불가',
                kakaoForm=kakaoForm
            )
        else:
            user.apply_delivery_address(address)

            KakaoInstantForm().Message(
                '사무실 등록이 완료되었습니다.',
                '등록된 사무실: {}호'.format(address),
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
