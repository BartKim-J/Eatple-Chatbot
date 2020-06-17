# View-System
from eatple_app.views_system.include import *
from eatple_app.views_system.debugger import *

# # # # # # # # # # # # # # # # # # # # # # # # #
#
# Static View
#
# # # # # # # # # # # # # # # # # # # # # # # # #


def component_B2B_Home(kakaoForm, orderManager, user):
    orderList = orderManager.getAvailableOrders().filter(Q(ordersheet__user=user))
    orderCount = orderList.count()
    order = orderList.first()

    lunchPurchaed = orderManager.getAvailableLunchOrder().filter(
        Q(ordersheet__user=user)).exists()

    if(lunchPurchaed):
        buttons = [
            {
                'action': 'block',
                'label': '주문내역 확인',
                'messageText': KAKAO_EMOJI_LOADING,
                'blockId': KAKAO_BLOCK_USER_EATPLE_PASS,
                'extra': {
                    KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_HOME
                }
            },
        ]
    else:
        buttons = [
            {
                'action': 'block',
                'label': '점심 보러가기',
                'messageText': KAKAO_EMOJI_LOADING,
                'blockId': KAKAO_BLOCK_USER_GET_STORE,
                'extra': {
                    KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_HOME
                }
            },
        ]

    # LUNCH HEADER
    lunchHomeImg = '{}{}'.format(HOST_URL, user.company.logoImgURL())

    thumbnail = {
        'imageUrl': lunchHomeImg,
        'fixedRatio': 'true',
        'width': 800,
        'height': 800,
    }

    kakaoForm.BasicCard_Push(
        '{} 카드입니다.'.format(user.company.name),
        '점심은 사내에서 픽업하세요.',
        thumbnail,
        buttons
    )


def kakaoView_B2B_Home(user, address):
    EatplusSkillLog('Home B2B')

    kakaoForm = KakaoForm()

    QUICKREPLIES_MAP = [
        {
            'action': 'block',
            'label': '최근 주문내역',
            'messageText': KAKAO_EMOJI_LOADING,
            'blockId': KAKAO_BLOCK_USER_ORDER_DETAILS,
            'extra': {
                KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_HOME
            }
        },
    ]

    # MAP
    addressMap = address.split()

    orderManager = UserOrderManager(user)
    orderManager.orderPenddingCleanUp()
    orderManager.availableOrderStatusUpdate()

    component_B2B_Home(kakaoForm, orderManager, user)

    kakaoForm.BasicCard_Add()

    kakaoForm.QuickReplies_AddWithMap(QUICKREPLIES_MAP)

    return JsonResponse(kakaoForm.GetForm())
