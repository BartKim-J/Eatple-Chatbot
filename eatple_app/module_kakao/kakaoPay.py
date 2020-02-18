# Define
from eatple_app.define import *

# Django Library
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

# Models
from eatple_app.models import *


class KakaoPay():
    def PushOrderSheet(self):
        headers = {
            'Authorization': 'KakaoAK {app_key}'.format(app_key=KAKAO_ADMIN_KEY),
        }

        data = {
            'cid': 'CADONE0860',

            'partner_order_id': '1',
            'partner_user_id': '1234',

            'item_name': '가결제 메뉴명',
            'item_code': '초코파이',

            'quantity': 1,

            'total_amount': 2200,
            'vat_amount': 200,

            'tax_free_amount': 0,

            'approval_url': 'https://developers.kakao.com/success',
            'cancel_url': 'https://developers.kakao.com/fail',
            'fail_url': 'https://developers.kakao.com/cancel',
        }

        apiURL = '{shcme}{host}{url}'.format(
            shcme='https://', host='kapi.kakao.com', url='/v1/payment/ready')

        print(apiURL)

        try:
            kakaoResponse = requests.post(apiURL, data=data, headers=headers)

        except kakaoResponse.HttpError as http_error:
            print(http_error.code)
            print(http_error.reason)

        print(kakaoResponse.status_code)
        print(kakaoResponse.text)

        return kakaoResponse
