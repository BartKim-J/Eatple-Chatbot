# Django Library
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

# Models
from eatple_app.models import *

# Define
from eatple_app.define import *

from eatple_app.apis.slack.slack_logger import SlackLogSignUp

# Modules
from eatple_app.module_kakao.responseForm import *
from eatple_app.module_kakao.requestForm import *
from eatple_app.module_kakao.kakaoPay import *
from eatple_app.module_kakao.validation import *


class KakaoInstantForm():
    def Message(self, title='', content='', thumbnail={}, buttons=[], kakaoForm=None, prev_block_id=None):
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

    def EatplePassIssued(self, order, kakaoForm=None, prev_block_id=None):
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
                'label': '픽업 부탁하기',
                'messageText': KAKAO_EMOJI_LOADING,
                'blockId': KAKAO_BLOCK_USER_ORDER_SHARING_START,
                'extra': {
                    KAKAO_PARAM_ORDER_ID: order.order_id,
                    KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_EATPLE_PASS
                }
            },
        ]

        isCafe = order.store.category.filter(name="카페").exists()
        if(isCafe):
            pickupTimeStr = dateByTimeZone(order.pickup_time).strftime(
                '%-m월 %-d일 오전 11시 30분 ~ 오후 4시')
        else:
            buttons.append({
                'action': 'block',
                'label': '픽업 시간 변경',
                'messageText': KAKAO_EMOJI_LOADING,
                'blockId': KAKAO_BLOCK_USER_EDIT_PICKUP_TIME,
                'extra': {
                    KAKAO_PARAM_ORDER_ID: order.order_id,
                    KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_EATPLE_PASS
                }
            })
            pickupTimeStr = dateByTimeZone(order.pickup_time).strftime(
                '%-m월 %-d일 %p %-I시 %-M분').replace('AM', '오전').replace('PM', '오후')

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

    def EatplePass(self, order, kakaoForm=None, prev_block_id=None):
        if(kakaoForm == None):
            kakaoForm = KakaoForm()

    def OrderList(self, order, kakaoForm=None, prev_block_id=None):
        if(kakaoForm == None):
            kakaoForm = KakaoForm()

        thumbnail = {
            'imageUrl': '{}{}'.format(HOST_URL, order.menu.imgURL()),
            'fixedRatio': 'true',
            'width': 800,
            'height': 800,
        }

        isCafe = order.store.category.filter(name="카페").exists()
        if(isCafe):
            pickupTimeStr = dateByTimeZone(order.pickup_time).strftime(
                '%-m월 %-d일 오전 11시 30분 ~ 오후 4시')
        else:
            pickupTimeStr = dateByTimeZone(order.pickup_time).strftime(
                '%-m월 %-d일 %p %-I시 %-M분').replace('AM', '오전').replace('PM', '오후')

        kakaoForm.BasicCard_Push(
            '{}'.format(order.menu.name),
            '픽업 시간: {}\n주문 상태: {}'.format(
                pickupTimeStr,
                dict(ORDER_STATUS)[order.status]
            ),
            thumbnail,
            []
        )

    def MenuList(self, menu, subText='', thumbnail={}, buttons=[], kakaoForm=None, prev_block_id=None):
        if(kakaoForm == None):
            kakaoForm = KakaoForm()

        profile = {
            "nickname": '{} - {}'.format(
                menu.store.name,
                subText,
            ),
            "imageUrl": '{}{}'.format(HOST_URL, menu.store.logoImgURL()),
        }

        thumbnails = [
            thumbnail,
        ]

        kakaoForm.ComerceCard_Push(
            _description=menu.description,
            _price=menu.price,
            _discount=None,
            _thumbnails=thumbnails,
            _profile=profile,
            _buttons=buttons
        )

        return JsonResponse(kakaoForm.GetForm())
