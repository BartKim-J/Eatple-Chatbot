# View-System
from eatple_app.views_system.include import *
from eatple_app.views_system.debugger import *

from eatple_app.apis.slack.slack_logger import SlackLogSignUp


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

        thumbnail = {
            'imageUrl': '{}{}'.format(HOST_URL, EATPLE_PASS_IMG_01),
        }

        buttons = [
            {
                'action': 'block',
                'label': '사장님께 확인받기',
                'messageText': KAKAO_EMOJI_LOADING,
                'blockId': KAKAO_BLOCK_USER_GET_USE_EATPLE_PASS_CONFIRM,
                'extra': {
                    KAKAO_PARAM_ORDER_ID: order.order_id,
                    KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_EATPLE_PASS
                }
            },
            {
                'action': 'block',
                'label': '주문취소',
                'messageText': KAKAO_EMOJI_LOADING,
                'blockId': KAKAO_BLOCK_USER_POST_ORDER_CANCEL,
                'extra': {
                    KAKAO_PARAM_ORDER_ID: order.order_id,
                    KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_EATPLE_PASS
                }
            }
        ]

        ORDER_LIST_QUICKREPLIES_MAP = [
            {
                'action': 'block',
                'label': '🏠  홈',
                'messageText': KAKAO_EMOJI_LOADING,
                'blockId': KAKAO_BLOCK_USER_HOME,
                'extra': {}
            },
        ]

        isPickupZone = order.menu.tag.filter(name="픽업존").exists()
        isCafe = order.store.category.filter(name="카페").exists()
        if(isCafe):
            pickupTimeStr = dateByTimeZone(order.pickup_time).strftime(
                '%-m월 %-d일 오전 11시 30분 ~ 오후 2시')
        else:
            pickupTimeStr = dateByTimeZone(order.pickup_time).strftime(
                '%-m월 %-d일 %p %-I시 %-M분').replace('AM', '오전').replace('PM', '오후')

            pickupTimes = order.menu.pickup_time.filter(
                selling_time=order.menu.selling_time)

            if(pickupTimes.count() > 1):
                ORDER_LIST_QUICKREPLIES_MAP.append({
                    'action': 'block',
                    'label': '픽업 시간 변경',
                    'messageText': KAKAO_EMOJI_LOADING,
                    'blockId': KAKAO_BLOCK_USER_EDIT_PICKUP_TIME,
                    'extra': {
                        KAKAO_PARAM_ORDER_ID: order.order_id,
                        KAKAO_PARAM_PREV_BLOCK_ID: KAKAO_BLOCK_USER_EATPLE_PASS
                    }
                })

        kakaoForm.BasicCard_Push(
            '{}'.format(order.menu.name),
            '주문번호: {}\n - 주문자: {}({})\n\n - 매장: {}\n - 주문 상태: {}\n\n - 픽업 시간: {}\n * 주문취소 가능시간: 오전 11시까지'.format(
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

        if(isPickupZone):
            kakaoForm.BasicCard_Push(
                '직접 픽업이 어려울땐, “픽업 부탁하기”로 함께 주문한 동료에게 부탁해보세요',
                '',
                {},
                [
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
            )
            kakaoForm.BasicCard_Add()
        elif(order.menu.selling_time == SELLING_TIME_LUNCH):
            # @B2B
            if(isB2BUser(order.ordersheet.user)):
                pass
            else:
                kakaoForm.BasicCard_Push(
                    '직접 픽업이 어려울땐, “픽업 부탁하기”로 함께 주문한 동료에게 부탁해보세요',
                    '',
                    {},
                    [
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
                        {
                            'action': 'webLink',
                            'label': '📍  매장 위치',
                            'webLinkUrl': kakaoMapUrl,
                        }
                    ]
                )
                kakaoForm.BasicCard_Add()
        elif(order.menu.selling_time == SELLING_TIME_DINNER):
            pass
        else:
            pass

        kakaoForm.QuickReplies_AddWithMap(ORDER_LIST_QUICKREPLIES_MAP)

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
                '%-m월 %-d일 오전 11시 30분 ~ 오후 2시')
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

        discount = menu.price_origin - menu.price

        kakaoForm.ComerceCard_Push(
            _description=menu.description,
            _price=menu.price + discount,
            _discount=discount,
            _thumbnails=thumbnails,
            _profile=profile,
            _buttons=buttons
        )

        return JsonResponse(kakaoForm.GetForm())

    def StoreList(self, store, subText='', description='', thumbnail={}, buttons=[], kakaoForm=None, prev_block_id=None):
        if(kakaoForm == None):
            kakaoForm = KakaoForm()

        kakaoForm.BasicCard_Push(
            '매장: {} - {}'.format(store.name, subText),
            '{}'.format(description),
            thumbnail,
            buttons
        )

        return JsonResponse(kakaoForm.GetForm())
