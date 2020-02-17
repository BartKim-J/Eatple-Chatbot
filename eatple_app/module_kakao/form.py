# Django Library
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

# Models
from eatple_app.models import *

# Define
from eatple_app.define import *

from eatple_app.views_slack.slack_logger import SlackLogSignUp

# Modules
from eatple_app.module_kakao.reponseForm import *
from eatple_app.module_kakao.requestForm import *
from eatple_app.module_kakao.kakaoPay import *
from eatple_app.module_kakao.validation import *


class KakaoInstantForm():
    def Message(self, title='', content='', thumbnail={}, buttons=[], kakaoForm=None):
        if(kakaoForm == None):
            kakaoForm = KakaoForm()

        kakaoForm.BasicCard_Push(
            title,
            content,
            thumbnail,
            buttons
        )
        kakaoForm.BasicCard_Add()

        return JsonResponse(kakaoForm.GetForm())

    def EatplePass(self, order, pickupTimeStr='', kakaoForm=None):
        if(kakaoForm == None):
            kakaoForm = KakaoForm()

        kakaoMapUrl = 'https://map.kakao.com/link/map/{name},{place}'.format(
            name=order.store.name,
            place=order.store.place
        )

        kakaoMapUrlAndriod = 'http://m.map.kakao.com/scheme/route?ep={place}&by=FOOT'.format(
            place=order.store.place
        )

        kakaoMapUrlIOS = 'http://m.map.kakao.com/scheme/route?ep={place}&by=FOOT'.format(
            place=order.store.place
        )

        thumbnail = {
            'imageUrl': '{}{}'.format(HOST_URL, EATPLE_PASS_IMG_01),
        }

        buttons = [
            {
                'action': 'block',
                'label': '사용하기(사장님 전용)',
                'messageText': KAKAO_EMOJI_LOADING,
                'blockId': KAKAO_BLOCK_USER_GET_USE_EATPLE_PASS_CONFIRM,
                'extra': {
                    KAKAO_PARAM_ORDER_ID: order.order_id,
                    KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_EATPLE_PASS
                }
            },
            {
                'action': 'block',
                'label': '부탁하기',
                'messageText': KAKAO_EMOJI_LOADING,
                'blockId': KAKAO_BLOCK_USER_ORDER_SHARING_START,
                'extra': {
                    KAKAO_PARAM_ORDER_ID: order.order_id,
                    KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_EATPLE_PASS
                }
            },
        ]

        kakaoForm.BasicCard_Push(
            '{}'.format(order.menu.name),
            '주문번호: {}\n - 주문자: {}({})\n\n - 매장: {}\n - 주문 상태: {}\n\n - 픽업 시간: {}'.format(
                order.order_id,
                order.ordersheet.user.nickname,
                str(order.ordersheet.user.phone_number)[9:13],
                order.store.name,
                dict(ORDER_STATUS)[order.status],
                pickupTimeStr,
            ),
            thumbnail,
            buttons
        )
        kakaoForm.BasicCard_Add()

        kakaoForm.BasicCard_Push(
            '{}'.format(order.store.addr),
            '',
            {},
            [
                {
                    'action': 'osLink',
                    'label': '길찾기',
                    'osLink': {
                        'android': kakaoMapUrlAndriod,
                        'ios': kakaoMapUrlIOS,
                        'pc': kakaoMapUrl,
                    }
                },
            ]
        )
        kakaoForm.BasicCard_Add()

        return JsonResponse(kakaoForm.GetForm())

    def EatplePassDelegated(self, order, pickupTimeStr='', kakaoForm=None):
        kakaoForm.BasicCard_Push(
            '{}'.format(order.menu.name),
            '주문번호: {}\n - 주문자: {}\n - 총 잇플패스 : {}개\n\n - 매장: {}\n - 주문 상태: {}\n\n - 픽업 시간: {}'.format(
                order.order_id,
                nicknameList,
                delegatedEatplePass.count() + ownEatplePass.count(),
                order.store.addr,
                pickupTimeStr,
                dict(ORDER_STATUS)[order.status]
            ),
            thumbnail,
            buttons
        )
    def MenuList(self, menu, subText='', thumbnail={}, buttons=[], kakaoForm=None):
        if(kakaoForm == None):
            kakaoForm = KakaoForm()

        kakaoForm.BasicCard_Push(
            '{} - {}'.format(
                menu.store.name,
                subText,
            ),
            '{}'.format(
                menu.description,
            ),
            thumbnail,
            buttons
        )

        return JsonResponse(kakaoForm.GetForm())
