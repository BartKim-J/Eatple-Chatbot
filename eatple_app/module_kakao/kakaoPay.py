# Define
from eatple_app.define import *

# Django Library
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

# Models
from eatple_app.models import *

# Modules
from eatple_app.module_kakao.reponseForm import *
from eatple_app.module_kakao.requestForm import *
from eatple_app.module_kakao.kakaoPay import *
from eatple_app.module_kakao.form import *
from eatple_app.module_kakao.validation import *

class KakaoPay():
    def PushOrderSheet(self, user, order=None):
        headers = {
            'Authorization': 'KakaoAK {app_key}'.format(app_key=KAKAO_ADMIN_KEY),
        }

        data = {
            # 'cid': 'CADONE0860',
            'cid': 'TC0ONETIME',

            'partner_order_id': 'EP0000',
            'partner_user_id': user.app_user_id,

            'item_name': '질할브로스',
            'item_code': 'EP0401',

            'quantity': 1,

            'total_amount': 6000,
            'vat_amount': 200,

            'tax_free_amount': 0,

            # 'approval_url': 'https://www.eatple.com:8000/success',
            # 'cancel_url': 'https://www.eatple.com:8000/fail',
            # 'fail_url': 'https://www.eatple.com:8000/cancel',

            'approval_url': 'https://developers.kakao.com/success',
            'cancel_url': 'https://developers.kakao.com/fail',
            'fail_url': 'https://developers.kakao.com/cancel',
        }

        apiURL = '{shcme}{host}{url}'.format(
            shcme='https://', host='kapi.kakao.com', url='/v1/payment/ready')

        try:
            kakaoResponse = requests.post(apiURL, data=data, headers=headers)

        except kakaoResponse.HttpError as http_error:
            print(http_error.code)
            print(http_error.reason)

        print('Header : ', kakaoResponse.headers)
        print('URL : ', kakaoResponse.url)
        print('STATUS : ', kakaoResponse.status_code)
        print('TEXT : ', kakaoResponse.text)

        andriodAppLink = json.loads(kakaoResponse.text)['android_app_scheme']
        iosAppLink = json.loads(kakaoResponse.text)['ios_app_scheme']

        print(andriodAppLink)
        print(iosAppLink)

        buttons = [
            {
                'action': 'osLink',
                'label': '결제하기',
                'osLink': {
                    'android': andriodAppLink,
                    'ios': iosAppLink,
                }
            },
        ]

        return KakaoInstantForm().Message(
            '카카오 페이 테스트',
            '결제 완료후 눌러주세요.',
            buttons=buttons,
        )
